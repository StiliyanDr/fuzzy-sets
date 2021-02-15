import matplotlib.pyplot as plt
import numpy as np

from fuzzysets import utils
from fuzzysets.sets.base import FuzzySet
from fuzzysets.sets.continuous import ContinuousFuzzySet
from fuzzysets.sets.finite import FiniteFuzzySet
from fuzzysets.tfn import TriangularFuzzyNumber as TFN


_X_LIMITS = (0., 10.)


_Y_LABEL = "μ(x)"


def plot_tfn_operations(first_name="A",
                        second_name="B",
                        x_lim=_X_LIMITS):
    lhs, rhs = _read_numbers(x_lim, first_name, second_name)

    if (lhs is not None and rhs is not None):
        figure, ((ax_add, ax_sub), (ax_mul, ax_div)) = \
            plt.subplots(2, 2)
        _set_up_and_plot_on(ax_add,
                            lhs + rhs,
                            f"{first_name} + {second_name}")
        _set_up_and_plot_on(ax_sub,
                            lhs - rhs,
                            f"{first_name} - {second_name}")
        _set_up_and_plot_on(ax_mul,
                            lhs * rhs,
                            f"{first_name} * {second_name}")
        _set_up_and_plot_on(ax_div,
                            lhs / rhs,
                            f"{first_name} / {second_name}")
        plt.show()


def _read_numbers(x_lim, first_name, second_name):
    plt.xlim(*x_lim)
    plt.ylim(0., 1.)
    plt.autoscale(False)

    first = _read_number(first_name)
    second = None

    if (first is not None):
        second = _read_number(second_name)

    return (first, second)


def _read_number(name):
    _prompt("Click to start the definition a TFN.")
    key_was_pressed = plt.waitforbuttonpress()

    if (not key_was_pressed):
        while True:
            tfn = _do_read_tfn()
            lines = _plot_tfn_on(plt, tfn, name, add_legend=True)
            _prompt("Happy? Press a key for yes, mouse click for no.")

            if (plt.waitforbuttonpress()):
                return tfn
            else:
                for l in lines:
                    l.remove()
    else:
        return None


def _prompt(message):
    plt.title(message, fontsize=16)
    plt.draw()


def _do_read_tfn():
    pts = []
    tfn = None

    while (tfn is None):
        _prompt("Select 3 corners with mouse.")
        pts = np.asarray(plt.ginput(3, timeout=-1))

        if (len(pts) < 3):
            _prompt("Too few points, starting over")
        else:
            try:
                tfn = TFN.from_tuple(
                    tuple(sorted(p[0] for p in pts))
                )
            except Exception:
                _prompt("Invalid selection, starting over")

    return tfn


def _plot_tfn_on(obj, tfn, name, add_legend=False):
    return _plot_on(obj,
                    [tfn.left, tfn.peak, tfn.right],
                    [0., 1., 0.],
                    _full_name_for(tfn, name),
                    add_legend=add_legend)


def _plot_on(obj, xs, ys, label="", add_legend=False, connect=True):
    method = (obj.plot
              if (connect)
              else obj.scatter)
    lines = method(
        xs,
        ys,
        label=label
    )
    if (add_legend):
        obj.legend()

    return lines


def _full_name_for(tfn, name):
    components = ", ".join(f"{c:.2f}" for c in tfn)
    return f"{name} = ({components})"


def _set_up_and_plot_on(axes, tfn, name):
    _set_up(axes,
            x_lim=(tfn.left - 1., tfn.right + 1.),
            title=_full_name_for(tfn, name),
            y_label=_Y_LABEL)
    _plot_tfn_on(axes, tfn, name)


def _set_up(axes,
            x_lim=_X_LIMITS,
            title="",
            x_label="",
            y_label=""):
    axes.grid(True)
    axes.set_xlim(*x_lim)
    axes.set_ylim(0., 1.)
    axes.set_title(title)
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)


def plot_fuzzy_set_operations(a,
                              b,
                              a_name="A",
                              b_name="B",
                              t_norm=min,
                              s_norm=max,
                              comp=utils.complement):
    if (isinstance(a, FuzzySet) and
        type(a) == type(b) and
        a.domain == b.domain):
        intersection = a.t_norm(b, t_norm)
        union = a.s_norm(b, s_norm)
        a_complement = a.complement(comp)
        b_complement = b.complement(comp)

        _, ((ax_a, ax_b), (ax_t_norm, ax_s_norm)) = \
            plt.subplots(2, 2)
        _set_up_and_plot_complement_on(ax_a, a, a_complement, a_name)
        _set_up_and_plot_complement_on(ax_b, b, b_complement, b_name)
        _set_up_and_plot_norm_on(ax_t_norm,
                                 a,
                                 b,
                                 intersection,
                                 a_name,
                                 b_name,
                                 norm_name="t")
        _set_up_and_plot_norm_on(ax_s_norm,
                                 a,
                                 b,
                                 union,
                                 a_name,
                                 b_name,
                                 norm_name="s")
        plt.show()


def _set_up_and_plot_complement_on(axes, s, s_complement, name):
    connect = isinstance(s, ContinuousFuzzySet)
    complement_name = f"¬({name})"
    xs = np.array(list(s.domain))
    _set_up(axes,
            x_lim=_x_limits_for(xs, s),
            title="Complement",
            y_label=_Y_LABEL)
    _plot_on(axes,
             xs,
             np.array(list(s.range)),
             label=name,
             connect=connect)
    _plot_on(axes,
             xs,
             np.array(list(s_complement.range)),
             label=complement_name,
             add_legend=True,
             connect=connect)


def _set_up_and_plot_norm_on(axes,
                             a,
                             b,
                             norm,
                             a_name,
                             b_name,
                             norm_name):
    connect = isinstance(a, ContinuousFuzzySet)
    norm_set_name = f"{norm_name}({a_name}, {b_name})"
    xs = np.array(list(a.domain))
    _set_up(axes,
            x_lim=_x_limits_for(xs, norm),
            title=f"{norm_name}-norm",
            y_label=_Y_LABEL)
    _plot_on(axes,
             xs,
             np.array(list(a.range)),
             label=a_name,
             connect=connect)
    _plot_on(axes,
             xs,
             np.array(list(b.range)),
             label=b_name,
             connect=connect)
    _plot_on(axes,
             xs,
             np.array(list(norm.range)),
             label=norm_set_name,
             add_legend=True,
             connect=connect)


def plot_fuzzy_set(s, title="", x_label="x", y_label=_Y_LABEL):
    if (isinstance(s, FuzzySet)):
        _, axes = plt.subplots()
        xs = np.array(list(s.domain))
        ys = np.array(list(s.range))
        _set_up(axes,
                x_lim=_x_limits_for(xs, s),
                title=title,
                x_label=x_label,
                y_label=y_label)
        _plot_on(axes,
                 xs,
                 ys,
                 connect=isinstance(s, ContinuousFuzzySet))
        plt.show()


def _x_limits_for(xs, s):
    return ((0., float(len(xs)) + 1.)
            if (isinstance(s, FiniteFuzzySet) or
                len(xs) == 0)
            else (xs[0] - 0.5, xs[-1] + 0.5))
