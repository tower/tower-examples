# Interactive Marimo Notebook

This app demonstrates how to run an interactive Marimo notebook in Tower. 

# How to use this demo

1. Install the project requirements: `uv sync`.
1. Login to Tower: `tower login`.
1. Deploy the app: `tower deploy`.
1. Go into the Tower UI and then into the app settings for this app. Toggle external accessibility (this is required to be able to visit your interactive app in Tower).
1. Go to the newly created URL on the app page.

Upon visiting the URL, a run of your app will automatically start and you will soon be directed to the interactive notebook.

# Making changes

You can modify the plot, the slider, etc. by editing [`./notebook.py`](./notebook.py). When you're done, redeploy your app and visit the URL again, and you'll see your updates!