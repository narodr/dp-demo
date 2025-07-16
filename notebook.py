import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium", app_title="")


@app.cell
def _():
    import marimo as mo
    import utils.plot as plot
    import utils.dp as dp
    import numpy as np
    import pandas as pd
    return dp, mo, np, pd, plot


@app.cell
def _(mo):
    mo.md(
        r"""
    # Privacidad diferen... ¿qué?

    La privacidad diferencial no es algo nuevo. Apareció por primera vez en [(Dwork, 2006)](https://dl.acm.org/doi/10.1007/11787006_1)
    como una herramienta matemática para medir el nivel de privacidad de un mecanismo sobre los datos que utiliza. —Espera, espera ¿qué es un mecanismo?— Bien, por mecanismo nos referimos a cualquier función o algoritmo que espere un **conjunto de datos** como entrada. Con esta definición tan vaga las opciones son casi ilimitadas. En efecto, la privacidad diferencial se ha utilizado en multitud de casos a lo largo de los años:

    - Cálculo de estadísticas básicas: conteo, media, etc.
    - Anonimización de datos y generación de datos sintéticos
    - Entrenamiento de modelos estadísticos, ML, etc.

    En resumen:

    > Un mecanismo será diferencialmente privado si sus salidas son indistinguibles
    para cualquier par de entradas que difieran en un único elemento. Matemáticamente, dados dos conjuntos de datos $D$ y $D'$:
    > $$\frac{p(f(D))}{p(f(D'))}\leq e^{\epsilon}$$
    """
    )
    return


@app.cell
def _(mo):
    data = mo.sql(
        f"""
        SELECT 
            *,
            CASE
                WHEN age > 0 AND age <= 20 THEN '0-20'
                WHEN age > 20 AND age <= 40 THEN '21-40'
                WHEN age > 40 AND age <= 60 THEN '41-60'
                WHEN age > 60 AND age <= 80 THEN '61-80'
                WHEN age > 80 AND age <= 100 THEN '81-100'
                ELSE NULL
            END AS binned_age
        FROM read_csv("data/PUMS.csv")
        """
    )

    mo.accordion(
        {
            "Datos brutos": data
        }
    )
    return (data,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Primer ejemplo: conteo

    La situación es esta: queremos publicar una estadística
    """
    )
    return


@app.cell
def _(mo):
    epsilon = mo.ui.slider(0.1, 10, 0.1, label="ε")
    epsilon
    return (epsilon,)


@app.cell
def _(mo):
    alpha = mo.ui.slider(0.01, 0.1, 0.01, label="α")
    alpha
    return (alpha,)


@app.cell
def _(epsilon, mo):
    mo.md(f"""El parámetro épsilon = {epsilon.value} mide de manera inversa el nivel de privacidad: A menor epsilon, mayor será la privacidad que ofrece del mecanismo.""")
    return


@app.cell
def _(alpha, data, dp, epsilon, mo):
    query = """
    SELECT binned_age, COUNT(*)
    FROM PUMS.PUMS
    GROUP BY binned_age
    """

    df = dp.compute_all_stats(epsilon.value, alpha.value, 
                              data=data,
                              query=query,
                              meta_path='data/PUMS.yaml'
                             )

    mo.ui.table(df, freeze_columns_left= ["Age bin", "Exact result", "Noised result"])
    return (query,)


@app.cell
def _(alpha, data, dp, epsilon, np, pd, query):
    x = np.linspace(epsilon.start, epsilon.stop, num = int((epsilon.stop - epsilon.start) / epsilon.step))
    y = np.array([dp.get_abs_error(data, query, eps, alpha=alpha.value, meta_path='data/PUMS.yaml') for eps in x]) / 100.0
    line = pd.DataFrame({"epsilon": x, "percent_error": y})
    return (line,)


@app.cell
def _(alpha, epsilon, line, plot, query):
    chart = plot.gen_tradeoff_chart(epsilon.value, 
                           alpha.value, 
                           query, 
                           meta_path='data/PUMS.yaml',
                           line_plot_df=line
                          )

    chart
    return


if __name__ == "__main__":
    app.run()
