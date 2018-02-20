
import pygame

class RoundedBox:
    """
    RoundedBox will render rounded boxes from a skin.
    """

    def __init__(self, skin, tx, ty, tw, th, corner_size):
        """
        Arguments:
            skin -- Surface containing the UI skin.
            tx -- x-coordinate of the sub-area containing the borders.
            ty -- y-coordinate of the sub-area containing the borders.
            tw -- width of the sub-area containing the borders.
            th -- height of the sub-area containing the borders.
            corner_size -- Sample area for the corners. Must be less than
                           min(tw, th) / 2 - 1.
        """
        self.skin = skin
        self.tx = tx
        self.ty = ty
        self.tw = tw
        self.th = th
        self.corner_size = corner_size
        self.prev_state = None
        self.surface = None
        self.tile_background = False

    def render(self, dest_surface, x, y, w, h):

        # Rerender the surface only when a change is made.
        state = (self.tx, self.ty, self.tw, self.th, self.corner_size, x, y, w, h)
        if self.prev_state != state:
            self.redraw(w, h)
            self.prev_state = state

        dest_surface.blit(self.surface, (x, y))

    def redraw(self, w, h):
        # The process of drawing a rounded box from a skin texture is somewhat
        # complicated.  There are two parts that make up a rounded box: the
        # borders and the background.  The borders texture has a black interior
        # that serves as a mask for the background texture.  Since there's no
        # way to mask one texture onto another by a color key in pygame, it's a
        # bit tricky to achieve the desired results.
        #
        # The process below is to first draw the corners of the borders at a
        # 1:1 scale, then stretch the sides and interior to fill in the rest.
        # Then, the background texture is scaled to the desired size and masked
        # using the border's alpha. Finally, the border texture is drawn over
        # the background texture with a black colorkey for transparency.

        # Shorten variables.
        w = int(w / 2)
        h = int(h / 2)
        tx = self.tx
        ty = self.ty
        tw = self.tw
        th = self.th
        c = self.corner_size

        # Can't draw a rounded box that is smaller than the corners.
        assert(w >= c * 2)
        assert(h >= c * 2)

        # Create a new blank surface.
        borders = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
        borders.fill((0, 0, 0, 0))

        # Convenience function for blitting a sub-area of the skin onto the
        # borders surface.
        #
        # dest -- destination, tuple (x, y) or tuple (x, y, w, h)
        # area -- sub-area of skin relative to tx and ty, tuple (x, y, w, h)
        def blit(dest, area):
            # If dest includes a desired width and height we have to do some
            # extra work to stretch the sub-area.
            if len(dest) > 2:
                # Get the sub-area and scale it as desired.
                src = pygame.transform.scale(
                        self.skin.subsurface(
                            pygame.Rect(
                                tx * 2 + area[0] * 2,
                                ty * 2 + area[1] * 2,
                                area[2] * 2,
                                area[3] * 2)),
                            (int(dest[2] * 2), int(dest[3] * 2)))
                # Blit the sub-area onto the surface.
                borders.blit(src, (dest[0] * 2, dest[1] * 2))
            else:
                borders.blit(
                        self.skin,
                        (dest[0] * 2, dest[1] * 2),
                        pygame.Rect(
                            tx * 2 + area[0] * 2,
                            ty * 2 + area[1] * 2,
                            area[2] * 2,
                            area[3] * 2))

        #-----------------------------------------------------------------------
        # Step 1: Render the borders.

        # Corners.
        blit((    0,     0), (     0,      0, c, c))
        blit((w - c,     0), (tw - c,      0, c, c))
        blit((    0, h - c), (     0, th - c, c, c))
        blit((w - c, h - c), (tw - c, th - c, c, c))

        # Middle top and bottom.
        blit((c,     0, w - c * 2, c), (c,      0, tw - c * 2, c))
        blit((c, h - c, w - c * 2, c), (c, th - c, tw - c * 2, c))

        # Middle left and right.
        blit((    0, c, c, h - c*2), (     0, c, c, th - c * 2))
        blit((w - c, c, c, h - c*2), (tw - c, c, c, th - c * 2))

        # Middle.
        blit((c, c, w - c * 2, h - c * 2), (c, c, tw - c * 2, th - c * 2))

        #-----------------------------------------------------------------------
        # Step 2: Stretch or tile the background uniformly to match the
        # destination.
        background = None
        if self.tile_background:
            background = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
            background.fill((0, 0, 0, 0))
            for x in range(0, w + tw, tw):
                for y in range(0, h + tw, th):
                    background.blit(self.skin, (x * 2, y * 2), pygame.Rect(tx * 2 + tw * 2, ty * 2, tw * 2, th * 2))
        else:
            background = pygame.transform.scale(
                    self.skin.subsurface(
                        pygame.Rect(
                            tx * 2 + tw * 2,
                            ty * 2 + 0,
                            tw * 2,
                            th * 2)),
                        (w * 2, h * 2))

        #-----------------------------------------------------------------------
        # Step 3: Mask the background by copying the alpha values from the
        # borders surface.
        alphas = pygame.surfarray.pixels_alpha(background)
        mask = pygame.surfarray.pixels_alpha(borders)
        alphas[:] = mask
        # These lock the surfaces until freed so we free them asap.
        del mask
        del alphas

        #-----------------------------------------------------------------------
        # Step 4: Overlay the borders over of the background texture using
        # black as the color key. The borders must first be converted to a
        # surface with no alpha for a colorkey to work. Transparent pixels
        # become black as well allowing this to work as desired.
        borders = borders.convert()
        borders.set_colorkey(pygame.Color(0, 0, 0, 255))
        background.blit(borders, (0, 0))
        self.surface = background

