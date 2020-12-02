import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import linregress
from scipy import optimize
import numpy as np
import datasource


def mean_y_err(model, data, start, count):
    return np.mean(
        np.abs(model[start:start + count + 1] - data[start:start + count + 1]) / data[start:start + count + 1])


def mean_y_err_abs(model, data, start, count):
    return np.mean(np.abs(model[start:start + count + 1] - data[start:start + count + 1]))


def autofit_exp(x: np.array, y: np.array, y_offset: float, start: int, count: int) -> (
        np.array, float, float, float, float):
    slope, intercept, r_value, p_value, std_err = linregress(x[start:start + count + 1],
                                                             np.log(y[start:start + count + 1] - y_offset))
    model = np.exp(x * slope + intercept) + y_offset
    rel_err = mean_y_err(model, y, start, count)
    abs_err = mean_y_err_abs(model, y, start, count)
    return model, (slope, intercept), (rel_err, abs_err)


def autofit_poly(x: np.array, y: np.array, deg: int, start: int, count: int) -> (np.array, float, float):
    z = np.polyfit(x[start:start+count], y[start:start+count], deg)
    poly = np.poly1d(z)
    model = [ poly(a) for xx in x[start:start+count]]
    rel_err = mean_y_err(model, y, start, count)
    abs_err = mean_y_err_abs(model, y, start, count)
    return model, (rel_err, abs_err)

def autofit_exp_plot(time, y, start, count=None, end=None):
    assert (count is None and end is not None) or (count is not None and end is None)
    count = count if end is None else end - start
    end = start + count

    x = np.array((time - time[0]).dt.days)
    y = np.array(y)

    def autofit_exp_err(y_offset):
        _, _, (err_rel, err_abs) = autofit_exp(x, y, y_offset, start=start, count=count)
        return err_rel

    data_min = np.min(y[start:end])
    y_offset = optimize.fminbound(autofit_exp_err, 0, data_min)

    # y = []
    # err_rel = []
    # err_abs = []
    y, (slope, intersect), (err_rel, err_abs) = autofit_exp(x, y, y_offset, start=start, count=count)
    # y2, (err_rel2, err_abs2) = autofit_poly(x, y, 1, start, count)

    line = plt.plot(time, y,
                    label=f"model: $exp({np.around(slope, 4)}x + {int(intersect)}) + {int(y_offset)}$\n"
                          f"mean relative error {np.around(err_rel * 100, 3)}% \n"
                          f"({time[start].strftime('%Y-%m-%d')}"
                          f" - {time[end].strftime('%Y-%m-%d')})",
                    alpha=0.7)
    plt.axvspan(time[start], time[end], color=line[0].get_color(), alpha=0.05)
    return y, (slope, intersect), (err_rel, err_abs)


def x_axis_dates(ax=None, fig=None):
    """Helper function to format the x axis as dates.

    Input:
    ax:  An Axes instance or an iterable of Axes instances.
    Optional, defaults to plt.gca()
    fig: The Figure instance containing those Axes or Axeses
    Optional, defaults to plt.gcf()
    """
    if ax is None: ax = plt.gca()
    if fig is None: fig = plt.gcf()
    loc = mdates.AutoDateLocator()
    fmt = mdates.AutoDateFormatter(loc)
    try:
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(fmt)
    except AttributeError:
        for a in ax:
            # Fresh locators/formatters are needed for each instance
            loc = mdates.AutoDateLocator()
            fmt = mdates.AutoDateFormatter(loc)
            a.xaxis.set_major_locator(loc)
            a.xaxis.set_major_formatter(fmt)
    fig.autofmt_xdate()


if __name__ == '__main__':
    data = datasource.get_today_data()
    time = datasource.get_time_series(data)

    infected = data["kumulativni_pocet_nakazenych"] - data["kumulativni_pocet_vylecenych"] - data[
        "kumulativni_pocet_umrti"]
    smooth = infected.rolling(window=7).mean().round()[3:]

    autofit_exp_plot(time, smooth, start=224, end=235)
    model, _, _ = autofit_exp_plot(time, smooth, start=249, end=264)
    autofit_exp_plot(time, smooth, start=264, end=271)

    analyze_range = 8
    today = len(infected)

    # plt.axvline(time[today])
    today_weekday = time.dt.weekday[today]
    a = np.array(infected[7:-3][:-(today_weekday + 1 + 3)][-7 * analyze_range - 1:])
    b = np.array(smooth[7:][:-(today_weekday + 1 + 3)][-7 * analyze_range - 1:])
    c = (a[1:] - a[:-1])
    d = (b[1:] - b[:-1])
    week_pattern = ((c - d)).reshape(-1, 7).mean(axis=0)
    print(week_pattern)

    # print(time.dt.weekday[today - (7 * 8 + 1)])
    print(f"Prediction for tomorrow: {round((model[today + 2] - model[today + 1]))}")

    # exit()
    plt.title("Cumulative infected (tested) CZ")
    plt.plot(time[:len(smooth)], smooth, "gx", label="7 day window average on data\n(3 days history, 3 days future)")
    plt.plot(time[:len(infected)], infected, "r-", label="real data", alpha=0.4)
    plt.ylim(0, 160_000)
    plt.xlim(time[200], time[len(infected) + 5])
    #plt.axvline(time[len(infected)])
    x_axis_dates()
    plt.legend()
    plt.show()
