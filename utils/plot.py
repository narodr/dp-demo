import altair as alt
import marimo as mo


def gen_tradeoff_chart(epsilon_choice, alpha, query, meta_path, line_plot_df):  
  # Tutorial from https://altair-viz.github.io/gallery/multiline_tooltip.html
  source = line_plot_df
  # The basic line
  line_plot = alt.Chart(source) \
    .mark_line() \
    .encode(x='epsilon', y='percent_error')

  # Create a selection that chooses the nearest point & selects based on x-value
  nearest = alt.selection(type='single', nearest=True, on='mouseover',
                          fields=['epsilon'], empty='none')

  # Transparent selectors across the chart. This is what tells us
  # the x-value of the cursor
  selectors = alt.Chart(source).mark_point().encode(
      x='epsilon:Q',
      opacity=alt.value(0),
  ).add_selection(
      nearest
  )

  # Draw points on the line, and highlight based on selection
  points = line_plot.mark_point().encode(
      opacity=alt.condition(nearest, alt.value(1), alt.value(0))
  )

  # Draw text labels near the points, and highlight based on selection
  text = line_plot.mark_text(align='left', dx=5, dy=-5).encode(
      text=alt.condition(nearest, 'percent_error:Q', alt.value(' '))
  )

  # Draw a rule at the location of the selection
  rules = alt.Chart(source).mark_rule(color='gray').encode(
      x='epsilon:Q',
  ).transform_filter(
      nearest
  )

  # Draw a rule over the current epsilon selection
  # Guide: https://github.com/altair-viz/altair/issues/1124#issuecomment-417714535
  chosen_epsilon_rule = alt.Chart(source).mark_rule(color='red').encode(
      x='epsilon_choice:Q'
  ).transform_calculate(
    epsilon_choice=f"{epsilon_choice}"
  )

  chart = mo.ui.altair_chart(line_plot + selectors + points + rules + text + chosen_epsilon_rule)
  return chart
