import marimo

app = marimo.App()

# --- imports (define once, share via returns) ---
@app.cell
def _():
    import marimo as mo
    return mo

@app.cell
def _():
    import matplotlib.pyplot as plt
    return plt

# --- UI / content ---
@app.cell
def _(mo):
    mo.md("# 📊 Dashboard Example")
    return

@app.cell
def _(mo):
    slider = mo.ui.slider(0, 100, step=5, label="Select a value")
    slider  # show the widget
    return slider

@app.cell
def _(slider, plt, mo):
    n = max(slider.value, 1)
    fig, ax = plt.subplots()
    ax.plot(range(n), [x**0.5 for x in range(n)])
    ax.set_title(f"Square Root Plot (n = {slider.value})")
    ax.set_xlabel("x")
    ax.set_ylabel("sqrt(x)")

    # Option A: interactive matplotlib helper
    mo.mpl.interactive(fig)

    # Option B (non-interactive): just return/display the fig
    # fig

@app.cell
def _(slider, mo):
    mo.md(f"### Current value: **{slider.value}**")

