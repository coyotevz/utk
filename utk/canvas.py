# -*- coding: utf-8 -*-

"""
    utk.canvas
    ~~~~~~~~~~

    Low level objects that Screen draw.

    :copyright: 2011-2012 by Utk Authors
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

import logging
from collections import namedtuple

from utk.utils import (
    Rectangle, calc_text_pos, apply_target_encoding, trim_text_attr_cs,
    rle_product, rle_len, rle_append_modify, calc_width, isiterable,
)

log = logging.getLogger("utk.canvas")

_CanvasView = namedtuple("CanvasView", "left top cols rows attr canv")

class CanvasView(_CanvasView):
    __slots__ = ()

    def content(self):
        return self.canv.body_content(self.left, self.top, self.cols, self.rows, self.attr)

    def trim_rows(self, rows):
        return self._replace(rows=rows)

    def trim_top(self, trim):
        return self._replace(top=self.top+trim,
                             rows=self.rows-trim)

    def trim_left(self, trim):
        return self._replace(left=self.left+trim,
                             cols=self.cols-trim)

    def trim_cols(self, cols):
        return self._replace(cols=cols)


Shard = namedtuple("Shard", "rows cviews")
ShardBody = namedtuple("ShardBody", "done_rows content_iter cview")
ShardTail = namedtuple("ShardTail", "col_gap done_rows content_iter cview")


class CanvasError(Exception):
    pass


class Canvas(object):
    """Base class for canvases"""

    def __init__(self, left=0, top=0, cols=1, rows=1):
        self._shards = []
        self._childs = []
        self._parent = None
        self._area = Rectangle(left, top, cols, rows)
        self._update = set() # areas to update
        self._visible = False
        #self._dirty = True
        self.invalidate()
        log.debug("%s%r", self.__class__.__name__, tuple(self._area))

    # sortcuts
    left = property(lambda s: s._area.x)
    top = property(lambda s: s._area.y)
    cols = property(lambda s: s._area.width)
    rows = property(lambda s: s._area.height)

    cursor = property(lambda s: None)

    def add_child(self, child):
        child._parent = self
        if child._update:
            self._update.update(child._update)
            child._update.clear()
        self._childs.append(child)
        self.invalidate_area(child._area)

    def remove_child(self, child):
        if child in self._childs:
            self._childs.remove(child)
            self.invalidate_area(child._area)
        child._parent = None

    def set_parent(self, parent):
        self.unparent()
        parent.add_child(self)

    def unparent(self):
        if self._parent:
            self._parent.remove_child(self)

    def move_to(self, newleft=None, newtop=None):
        if not self._parent:
            return
        oldarea = self._area
        if newleft is None:
            newleft = oldarea.x
        if newtop is None:
            newtop = oldarea.y
        newarea = self._area._replace(x=newleft, y=newtop)

        if oldarea.x == newarea.x and oldarea.y == newarea.y:
            return

        self._area = newarea

        self._parent.invalidate_area(oldarea)
        self._parent.invalidate_area(newarea)

    def move(self, deltaleft=0, deltatop=0):
        self.move_to(self.left+deltaleft, self.top+deltatop)

    def resize(self, newwidth=None, newheight=None):
        log.debug("%s::resize(%d, %d)", repr(self), newwidth, newheight)
        oldarea = self._area
        if newwidth is None:
            newwidth = oldarea.width
        if newheight is None:
            newheight = oldarea.height

        newarea = self._area._replace(width=newwidth, height=newheight)

        if oldarea.width == newarea.width and oldarea.height == newarea.height:
            return

        self._area = newarea

        update_area = newarea.union(oldarea)
        self.invalidate_area(update_area)

    def move_resize(self, x, y, width, height):
        self.move_to(x, y)
        self.resize(width, height)

    @property
    def is_dirty(self):
        return self._dirty

    def _set_dirty(self):
        self._dirty = True
        if self._parent:
            self._parent._set_dirty()

    def _unset_dirty(self):
        self._dirty = False

    def invalidate_area(self, area):
        if self._parent:
            self._parent.invalidate_area(area)
        else:
            log.debug("%s::invalidate_area(%r)", repr(self), area)
            self._update.add(area)
        self._set_dirty()

    def invalidate(self):
        self.invalidate_area(self._area)

    def show(self):
        log.debug("Canvas::show()")
        self._visible = True
        self.invalidate()

    def hide(self):
        log.debug("Canvas::hide()")
        self._visible = False
        self.invalidate()

    @property
    def is_visible(self):
        return self._visible

    @property
    def shards(self):
        #if self.is_dirty:
        self.calculate_shards()
        return self._shards

    def calculate_shards(self):
        if not self.is_dirty:
            return

        log.debug("calculating shards in %s <%x>", repr(self), id(self))

        #if not self._shards:
        self._shards = [
            Shard(self.rows, [
                CanvasView(0, 0, self.cols, self.rows, None, self)
            ])
        ]


        updates = None
        if self._update:
            import pprint
            log.debug(pprint.pformat(self._update))
            for u in self._update:
                if not updates:
                    updates = u
                else:
                    updates = updates.union(u)
            self._update.clear()
            updates = updates._replace(x=max(updates.x, self._area.x),
                                       y=max(updates.y, self._area.y),
                                       width=min(updates.width, self._area.width),
                                       height=min(updates.height, self._area.height))
            log.debug("updates for '%s': %r", self._text, updates,)
        else:
            updates = self._area

        for child in self._childs:
            if not child._visible:
                continue
            width = child.cols
            height = child.rows
            left = child.left - self.left
            top = child.top - self.top
            right = self.cols - left - width
            bottom = self.rows - top - height

            shards = self._shards
            top_shards = []
            side_shards = self._shards
            bottom_shards = []
            if top:
                side_shards = shards_trim_top(shards, top)
                top_shards = shards_trim_rows(shards, top)
            if bottom:
                bottom_shards = shards_trim_top(side_shards, height)
                side_shards = shards_trim_rows(side_shards, height)

            left_shards = []
            right_shards = []
            if left:
                left_shards = [shards_trim_sides(side_shards, 0, left)]
            if right:
                right_shards = [shards_trim_sides(side_shards, left+width, right)]

            if not self.rows:
                middle_shards = []
            elif left or right:
                middle_shards = shards_join(left_shards + [child.shards] + right_shards)
            else:
                middle_shards = child.shards

            self._shards = top_shards + middle_shards + bottom_shards
        self._unset_dirty()

    def content(self):
        shard_tail = []
        for shard in self.shards:
            # combine shard and shard tail
            sbody = shard_body(shard.cviews, shard_tail)

            # output rows
            for i in range(int(shard.rows)):
                yield shard_body_row(sbody)

            # prepare next shard tail
            shard_tail = shard_body_tail(shard.rows, sbody)

    def body_content(self, trim_left=0, trim_top=0, cols=None, rows=None, attr=None):
        """Returns the canvas content as a list of rows where each row
        is a list of (attr, cs, text) tuples.

        trim_left, trim_top, cols, rows may be set by caller when
        rendering a partially obscure canvas.
        """
        raise NotImplementedError()


class SolidCanvas(Canvas):

    def __init__(self, fill_char, attr=None, left=0, top=0, cols=1, rows=1):
        end, col = calc_text_pos(fill_char, 0, len(fill_char), 1)
        assert col == 1, "Invalid fill_char: %r" % fill_char
        self._text, cs = apply_target_encoding(fill_char[:end])
        self._cs = cs[0][0]
        self._attr = None
        if attr and None in attr:
            self._attr = attr[None]
        super(SolidCanvas, self).__init__(left, top, cols, rows)

    def body_content(self, trim_left=0, trim_top=0, cols=None, rows=None, attr=None):
        if cols is None:
            cols = self.cols
        if rows is None:
            rows = self.rows

        line = [(self._attr, self._cs, self._text*cols)]
        for i in range(int(rows)):
            yield line

    def __repr__(self):
        return "<SolidCanvas('%s', left=%d, top=%d, cols=%d, rows=%d)>" % (self._text, self.left, self.top, self.cols, self.rows)


class TextCanvas(Canvas):
    """Class for storing rendered text attributes"""

    def __init__(self, text=None, attr=None, cs=None, left=0, top=0, cols=1, rows=1):
        if text is None:
            text = []
        elif not isiterable(text):
            text = [text]
        if attr is None:
            attr = [[] for x in range(len(text))]
        if cs is None:
            cs = [[] for x in range(len(text))]


        self._attr = attr
        self._cs = cs
        self._text = text

        super(TextCanvas, self).__init__(left, top, cols, rows)

    def body_content(self, trim_left=0, trim_top=0, cols=None, rows=None,
                     attr_map=None):
        log.debug("body_content for %s", self)
        if cols is None:
            cols = self.cols - trim_left
        if rows is None:
            rows = self.rows - trim_top

        assert trim_left >= 0 and trim_left < self.cols
        assert cols > 0 and trim_left + cols <= self.cols
        assert trim_top >= 0 and trim_top < self.rows
        assert rows > 0 and trim_top + rows <= self.rows

        text, attr, cs = self.pad_text_attr()

        if trim_top or rows < self.rows:
            text_attr_cs = zip(
                    text[trim_top:trim_top+rows],
                    attr[trim_top:trim_top+rows],
                    cs[trim_top:trim_top+rows])
        else:
            text_attr_cs = zip(text, attr, cs)

        rows_done = 0
        for text, attr, cs in text_attr_cs:
            if trim_left or cols < self.cols:
                text, attr, cs = trim_text_attr_cs(text, attr, cs, trim_left, trim_left+cols)
            attr_cs = rle_product(attr, cs)
            i = 0
            row = []
            for (a, cs), run in attr_cs:
                if attr_map and a in attr_map:
                    a = attr_map[a]
                row.append((a, cs, text[i:i+run]))
                i += run
            rows_done += 1
            yield row
        while rows_done < rows:
            yield [(None, None, str().rjust(cols))]

    def __repr__(self):
        return "<TextCanvas(%r, left=%d, top=%d, cols=%d, rows=%d)>" % (self._text, self.left, self.top, self.cols, self.rows)

    def pad_text_attr(self):
        attr = list(self._attr)
        cs = list(self._cs)
        text = list(self._text)
        maxcol = self.cols

        widths = []
        for t in text:
            widths.append(calc_width(t, 0, len(t)))

        for i in range(len(text)):
            w = widths[i]
            if w > maxcol:
                raise CanvasError("Canvas text is wider than the maxcol specified \n%r\n%r\n%r" % (maxcol, widths, text))
            if w < maxcol:
                text[i] = text[i] + str().rjust(maxcol-w)
            a_gap = len(text[i]) - rle_len(attr[i])
            if a_gap < 0:
                raise CanvasError("Attribute extends beyond text \n%r\n%r" % (text[i], attr[i]))
            if a_gap:
                rle_append_modify(attr[i], (None, a_gap))

            cs_gap = len(text[i]) - rle_len(cs[i])
            if cs_gap < 0:
                raise CanvasError("Character Set extends beyond text \n%r\n%r" % (text[i], cs[i]))
            if cs_gap:
                rle_append_modify(cs[i], (None, cs_gap))

        return text, attr, cs

class BlankCanvas(Canvas):

    def body_content(self, trim_left=0, trim_top=0, cols=None, rows=None, attr=None):
        if cols is None:
            cols = self.cols
        if rows is None:
            rows = self.rows

        def_attr = None
        if attr and None in attr:
            def_attr = attr[None]
        line = [(def_attr, None, str().rjust(cols))]
        for i in range(rows):
            yield line

    def show(self):
        log.debug("BlankCanvas::show()")
        self._visible = True
        for child in self._childs:
            child.show()
        self.invalidate()

    def __repr__(self):
        return "<BlankCanvas(cols=%d, rows=%d)>" % (self.cols, self.rows)

def shard_body_row(sbody):
    """
    Return one row, advancing the iterators in sbody.

    ** MODIFIES sbody by calling next() on its iterators **
    """
    row = []
    for done_rows, content_iter, cview in sbody:
        if content_iter:
            row.extend(next(content_iter))
        else:
            # need to skip this unchanged canvas
            if row and isinstance(row[-1], int):
                row[-1] = row[-1] + cview.cols
            else:
                row.append(cview.cols)
    return row


def shard_body_tail(num_rows, sbody):
    """
    Return a new shard tail that follows this shard body.
    """
    shard_tail = []
    col_gap = 0
    done_rows = 0
    for done_rows, content_iter, cview in sbody:
        done_rows += num_rows
        if done_rows == cview.rows:
            col_gap += cview.cols
            continue
        shard_tail.append(ShardTail(col_gap, done_rows, content_iter, cview))
        col_gap = 0
    return shard_tail


def shard_body(cviews, shard_tail, create_iter=True, iter_default=None):
    """
    Return a list of (done_rows, content_iter, cview) tuples for
    this shard and shard tail.

    If a canvas in cviews is None (eg. when unchanged from
    shard_cviews_delta()) or if create_iter is False then no
    iterator is created for content_iter.

    iter_default is the value used for content_iter when no iterator
    is created.
    """
    col = 0
    body = [] # build the next shard tail
    cviews_iter = iter(cviews)
    for col_gap, done_rows, content_iter, tail_cview in shard_tail:
        while col_gap:
            try:
                cview = next(cviews_iter)
            except StopIteration:
                raise CanvasError("cviews do not fill gaps in shard_tail!!!")
            col += cview.cols
            col_gap -= cview.cols
            if col_gap < 0:
                log.debug("col_gap = %d", col_gap)
                log.debug("body = %r", body)
                raise CanvasError("cviews overflow gaps in shard_tail!!!")
            if create_iter and cview.canv:
                new_iter = cview.content()
            else:
                new_iter = iter_default
            body.append(ShardBody(0, new_iter, cview))
        body.append(ShardBody(done_rows, content_iter, tail_cview))
    for cview in cviews_iter:
        if create_iter and cview.canv:
            new_iter = cview.content()
        else:
            new_iter = iter_default
        body.append(ShardBody(0, new_iter, cview))
    return body


def shards_trim_top(shards, top):
    """
    Return shards with top rows removed.
    """
    assert top > 0

    shard_iter = iter(shards)
    shard_tail = []
    # skip over shards that are completely removed
    for num_rows, cviews in shard_iter:
        if top < num_rows:
            break
        sbody = shard_body(cviews, shard_tail, False)
        shard_tail = shard_body_tail(num_rows, sbody)
        top -= num_rows
    else:
        raise CanvasError("tried to trim shards out of existence")

    sbody = shard_body(cviews, shard_tail, False)
    shard_tail = shard_body_tail(num_rows, sbody)
    # trim the top of this shard
    new_sbody = []
    for done_rows, content_iter, cv in sbody:
        new_sbody.append((0, content_iter, cv.trim_top(done_rows+top)))
    sbody = new_sbody

    new_shards = [Shard(num_rows-top, [cv for done_rows, content_iter, cv in sbody])]

    # write out the rest of the shards
    new_shards.extend(shard_iter)

    return new_shards


def shards_trim_rows(shards, keep_rows):
    """
    Return the topmost keep_rows rows from shards.
    """
    assert keep_rows >= 0, keep_rows

    new_shards = []
    done_rows = 0
    for num_rows, cviews in shards:
        if done_rows >= keep_rows:
            break
        new_cviews = []
        for cv in cviews:
            if cv.rows + done_rows > keep_rows:
                new_cviews.append(cv.trim_rows(keep_rows - done_rows))
            else:
                new_cviews.append(cv)

        if num_rows + done_rows > keep_rows:
            new_shards.append(Shard(keep_rows - done_rows, new_cviews))
        else:
            new_shards.append(Shard(num_rows, new_cviews))
        done_rows += num_rows

    return new_shards


def shards_trim_sides(shards, left, cols):
    """
    Return shards with starting from column left and cols total width.
    """
    assert left >= 0 and cols > 0, (left, cols)
    shard_tail = []
    new_shards = []
    right = left + cols
    for num_rows, cviews in shards:
        sbody = shard_body(cviews, shard_tail, False)
        shard_tail = shard_body_tail(num_rows, sbody)
        new_cviews = []
        col = 0
        for done_rows, content_iter, cv in sbody:
            next_col = col + cv.cols
            if done_rows or next_col <= left or col >= right:
                col = next_col
                continue
            if col < left:
                cv = cv.trim_left(left - col)
                col = left
            if next_col > right:
                cv = cv.trim_cols(right - col)
            new_cviews.append(cv)
            col = next_col
        if not new_cviews:
            prev_num_rows, prev_cviews = new_shards[-1]
            new_shards[-1] = Shard(prev_num_rows + num_rows, prev_cviews)
        else:
            new_shards.append(Shard(num_rows, new_cviews))
    return new_shards


def shards_join(shard_lists):
    """
    Return the result of joining shard lists horizontally.
    All shards lists must have the same number of rows.
    """
    shards_iters = [iter(sl) for sl in shard_lists]
    shards_current = [next(i) for i in shards_iters]

    new_shards = []
    while True:
        new_cviews = []
        num_rows = min([shard.rows for shard in shards_current])

        shards_next = []
        for shard in shards_current:
            if shard.cviews:
                new_cviews.extend(shard.cviews)
            shards_next.append(Shard(shard.rows - num_rows, None))

        shards_current = shards_next
        new_shards.append(Shard(num_rows, new_cviews))

        # advance to next shards
        try:
            for i in range(len(shards_current)):
                if shards_current[i].rows > 0:
                    continue
                shards_current[i] = next(shards_iters[i])
        except StopIteration:
            break
    return new_shards
