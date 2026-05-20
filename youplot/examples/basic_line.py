"""
Basic example — weather station telemetry over a 24-hour period.
Two synced charts via up.combine() / the + operator.

Run from the youplot parent directory:
    python -m youplot.examples.basic_line
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import math, time
import youplot as up


def make_data(n=1440, seed=7):
    base_ts = int(time.time()) - 86400
    ts_ms   = [(base_ts + i * 60) * 1000 for i in range(n)]

    def noise(scale, offset=0):
        import random; random.seed(seed + offset)
        return [random.gauss(0, scale) for _ in range(n)]

    def diurnal(lo, hi, phase=0):
        return [lo + (hi-lo)*0.5*(1-math.cos(2*math.pi*(i/n+phase))) for i in range(n)]

    temp_c    = [round(diurnal(14,31)[i] + noise(0.3,1)[i], 1) for i in range(n)]
    feels     = [round(temp_c[i] - 2.5 + 0.4*math.sin(i/120) + noise(1.5,2)[i], 1) for i in range(n)]
    humidity  = [round(max(10, min(100, diurnal(80,35,0.5)[i] + noise(2,3)[i])), 1) for i in range(n)]
    dew_point = [round(temp_c[i] - (100-humidity[i])/5 + noise(0.6,4)[i], 1) for i in range(n)]
    pressure  = [round(1012 + 6*math.sin(2*math.pi*i/n) + 3*math.cos(2*math.pi*i/(n*0.4)) + noise(0.4,5)[i], 1) for i in range(n)]
    wind_spd  = [round(max(0, 8 + 6*math.sin(i/180+1) + abs(noise(2,6)[i])), 1) for i in range(n)]

    day_frac  = lambda i: (i%n)/n
    solar     = [max(0, round(900*math.sin(math.pi*max(0,(day_frac(i)-0.25))/0.5)**1.2 + noise(15,7)[i], 0))
                 if 0.25 <= day_frac(i) <= 0.75 else 0 for i in range(n)]
    uv        = [round(max(0, min(11, solar[i]/80 + noise(0.2,8)[i])), 1) for i in range(n)]
    pm25      = [round(max(0, 12
                    + 20*math.exp(-((i-n*0.30)**2)/(2*(n*0.04)**2))
                    + 15*math.exp(-((i-n*0.75)**2)/(2*(n*0.04)**2))
                    + abs(noise(3,9)[i])), 1) for i in range(n)]
    rain = [0.0]*n
    sc = int(n*0.58)
    for i in range(n):
        d = i - sc
        if abs(d) < 60:
            rain[i] = round(max(0, 8*math.exp(-(d**2)/800) + noise(0.3,10)[i]), 2)

    return ts_ms, temp_c, feels, humidity, dew_point, pressure, wind_spd, solar, uv, pm25, rain


def main():
    ts_ms, temp_c, feels, humidity, dew_point, pressure, wind_spd, solar, uv, pm25, rain = make_data()
    n = len(ts_ms)

    # ── Chart 1: Temperature, Humidity, Wind, Pressure ───────────────────────
    fig1 = up.Figure(
        title="Temperature · Humidity · Wind · Pressure",
        subtitle="Hover to sync crosshair · drag to zoom · vertical drag zooms Y · annotate to pin notes",
        theme="light", height=300,
        y_label="Temp °C / Humidity % / Wind km·h⁻¹",
        y_right_label="Pressure hPa",
        zoom=True, legend=True,
    )
    fig1.line(ts_ms, temp_c,    label="Temp °C",       color="#f97316", width=2.5, hover_unit=" °C")
    fig1.line(ts_ms, feels,     label="Feels Like °C", color="#fb923c", width=1.5, dash=True, hover_unit=" °C")
    fig1.line(ts_ms, humidity,  label="Humidity %",    color="#38bdf8", width=2.0, fill=True, fill_opacity=0.07, hover_unit="%")
    fig1.line(ts_ms, dew_point, label="Dew Point °C",  color="#0ea5e9", width=1.5, dash=True, hover_unit=" °C")
    fig1.line(ts_ms, wind_spd,  label="Wind km/h",     color="#a3e635", width=1.5, hover_unit=" km/h")
    # fig1.line(ts_ms, pressure,  label="Pressure hPa",  color="#8b5cf6", width=1.5, axis="right", hover_unit=" hPa")

    fig1.band(y_lo=25, y_hi=35, label="Heat stress",    color="#f97316", opacity=0.07)
    fig1.band(y_lo=70, y_hi=100, label="High humidity", color="#38bdf8", opacity=0.06)

    fig1.region(x_start=ts_ms[0],           x_end=ts_ms[int(n*0.25)], color="#6366f1", opacity=0.04)
    fig1.region(x_start=ts_ms[int(n*0.88)], x_end=ts_ms[-1],          color="#6366f1", opacity=0.04)

    fig1.vline(x=ts_ms[int(n*0.25)], label="Sunrise", color="#f97316")
    fig1.vline(x=ts_ms[int(n*0.75)], label="Sunset",  color="#8b5cf6")
    fig1.hline(y=25, label="Heat threshold", color="#f97316", dash=True)
    fig1.hline(y=60, label="High humidity",  color="#38bdf8", dash=True)

    fig1.tag(x_start=ts_ms[int(n*0.28)], x_end=ts_ms[int(n*0.40)],
             label="Morning Rush", color="#f43f5e", removable=False)
    fig1.tag(x_start=ts_ms[int(n*0.72)], x_end=ts_ms[int(n*0.80)],
             label="Evening Peak", color="#8b5cf6", removable=True)

    # Code-defined annotation pins
    # fig1.pin(ts_ms[int(n*0.25)], label="Sunrise crossover", y_frac=0.15, color="#f97316")
    # fig1.pin(ts_ms[int(n*0.52)], label="Temp peak 31°C",   y_frac=0.05, color="#f43f5e")

    # ── Chart 2: Solar, Air Quality, Rain ────────────────────────────────────
    fig2 = up.Figure(
        title="Solar · Air Quality · Rain",
        subtitle="Crosshair synced with chart above",
        theme="light", height=300,
        y_label="Solar W/m² / UV / PM2.5 µg/m³",
        y_right_label="Rain mm/h",
        zoom=True, legend=True,
    )
    fig2.line(ts_ms, solar, label="Solar W/m²",   color="#facc15", width=2.0, fill=True, fill_opacity=0.08, hover_unit=" W/m²")
    fig2.line(ts_ms, uv,    label="UV Index",      color="#fbbf24", width=1.5, dash=True)
    fig2.line(ts_ms, pm25,  label="PM2.5 µg/m³",  color="#f43f5e", width=1.5, hover_unit=" µg/m³")
    fig2.line(ts_ms, rain,  label="Rain mm/h",     color="#06b6d4", width=1.5, fill=True, fill_opacity=0.15,
              axis="right", hover_unit=" mm/h")

    fig2.band(y_lo=35, y_hi=150, label="PM2.5 Unhealthy", color="#f43f5e", opacity=0.05)
    fig2.vline(x=ts_ms[int(n*0.58)], label="Peak Rain", color="#06b6d4", dash=True)
    fig2.hline(y=35, label="PM2.5 Moderate", color="#f43f5e", dash=True)
    fig2.tag(x_start=ts_ms[int(n*0.55)], x_end=ts_ms[int(n*0.62)],
             label="Afternoon Shower", color="#06b6d4", removable=False)



    dash = up.combine(fig1, fig2, title="Weather Station — 24h Overview")

    out = dash.save("/tmp/youplot_weather_demo.html")
    print(f"✓ Saved to {out}")
    dash.show()


if __name__ == "__main__":
    main()
