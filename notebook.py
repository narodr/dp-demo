import marimo

__generated_with = "0.14.10"
app = marimo.App(app_title="")


@app.cell
def _():
    import marimo as mo
    return (mo,)


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
def _(data, mo):
    mo.accordion(
        {
            "Datos brutos": data
        }
    )
    return


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
def _(epsilon, mo):
    mo.md(f"""El parámetro **épsilon** {epsilon} mide de manera inversa el nivel de privacidad: A menor epsilon, mayor será la privacidad que ofrece del mecanismo.""")
    return


@app.cell
def _(mo):
    epsilon = mo.ui.slider(0.1, 10, 0.1, label="ε")
    epsilon
    return (epsilon,)


@app.cell(hide_code=True)
def _(epsilon, mo):
    import utils.dp as dp

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

    query = """
    SELECT binned_age, COUNT(*)
    FROM PUMS.PUMS
    GROUP BY binned_age
    """
    unnoised_result=dp.get_unnoised_result(data)
    groupby_keys = sorted(list(unnoised_result.keys()))

    df = dp.compute_all_stats(epsilon.value, 0.05, groupby_keys=groupby_keys, data=data, query=query, meta_path='data/PUMS.yaml')
    df
    # mo.ui.table(data=df, pagination=False, freeze_columns_left=['Age bin', 'Exact result', 'Noised result'])
    return data, dp, query


@app.cell
def _(data, dp, epsilon, query):
    import utils.plot as plot
    import numpy as np
    import pandas as pd

    x = np.linspace(.1, 10, num = int((10 - .1) / .1))
    y = np.array([dp.get_abs_error(data, query, epsilon.value, .05, 'data/PUMS.yaml') for eps in x]) * 100.0
    line_plot_df = pd.DataFrame({"epsilon": x, "percent_error": y})

    plot.gen_tradeoff_chart(epsilon.value, line_plot_df)
    return


if __name__ == "__main__":
    app.run()
