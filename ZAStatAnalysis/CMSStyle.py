
def changeFont():
    """
    Change current font to Arial
    """

    from matplotlib import rc
    rc('font', **{'family': 'sans-serif', 'sans-serif':['Arial', 'Helvetica', 'Nimbus Sans L', 'Liberation Sans']})
    rc('mathtext', default='regular')

def applyStyle(fig, ax, lumi, extra='Preliminary', pos='out', figures=1):
    """
    Apply CMS style to a matplotlib figure

    Parameters:

    fig     The figure
    ax      The axes of the figure
    lumi    The integrated luminosity in /pb
    pos     The position of the texts. Can be 'out', 'upper_left', 'upper_right',
            'bottom_left', 'bottom_right'
    """

    def get_extra_label_position(text):
        ex = text.get_window_extent(renderer=fig.canvas.get_renderer())
        inv = fig.transFigure.inverted()

        if pos == 'out':
            extra_label_x = ex.x0 + ex.width

            # Convert to figure coordinates. We only care about the x, so use a dummy y
            extra_label_x, _ = inv.transform((extra_label_x, 0))

            return (extra_label_x + x_space_size, text.get_position()[1])
        else:
            return (text.get_position()[0], text.get_position()[1] - y_space_size)

    def get_extra_label_align():
        if pos == 'out':
            return ('left', 'baseline')
        elif 'left' in pos:
            return ('left', 'top')
        elif 'right' in pos:
            return ('right', 'top')


    fig.subplots_adjust(top=0.945)

    # Constants
    top_padding = 0.01
    x_space_size = 0.01
    y_space_size = 0.01

    # Get bounding box of axes, in Figure coordinates
    axes_bbox = ax.get_position()

    lumi_text_x = axes_bbox.x1
    lumi_text_y = axes_bbox.y1 + top_padding

    cms_text_ha = 'left'
    cms_text_va = 'baseline'

    if pos == 'out':

        cms_text_x = axes_bbox.x0
        cms_text_y = lumi_text_y

    elif pos == 'top_left':

        cms_text_x = axes_bbox.x0 + 0.03
        cms_text_y = axes_bbox.y1 - 0.06

    elif pos == 'top_right':

        cms_text_x = axes_bbox.x1 - 0.03
        cms_text_y = axes_bbox.y1 - 0.06
        cms_text_ha = 'right'

    elif pos == 'bottom_right':

        cms_text_x = axes_bbox.x1 - 0.03
        cms_text_y = axes_bbox.y0 + 0.06
        cms_text_ha = 'right'

    elif pos == 'bottom_left':

        cms_text_x = axes_bbox.x0 + 0.03
        cms_text_y = axes_bbox.y0 + 0.06

    # CMS text in bold
    cms_text = ax.text(cms_text_x, cms_text_y, 'CMS', transform=fig.transFigure, fontsize='x-large', fontweight='bold', va=cms_text_va, ha=cms_text_ha)

    extra_label_x, extra_label_y = get_extra_label_position(cms_text)
    extra_label_ha, extra_label_va = get_extra_label_align()

    # Extra label
    ax.text(extra_label_x, extra_label_y, extra, transform=fig.transFigure, fontsize='large', fontstyle='italic', va=extra_label_va, ha=extra_label_ha)

    # Finally, the luminosity
    if not lumi:
        fmt = "(13 TeV)"
    else:
        fmt = "{lumi:.{figures}f} $fb^{{-1}}$ (13 TeV)".format(lumi=(lumi / 1000.), figures=figures)

    ax.text(lumi_text_x, lumi_text_y, fmt, transform=fig.transFigure, fontsize='large', va='baseline', ha='right')

