# Miscellaneous Scripts

This is a collection of various scripts that tackle specific obstacles I've encountered over the last couple years. Unlike the [facebook_tools](https://github.com/aliavictor/portfolio/tree/main/facebook_tools) and [google_tools](https://github.com/aliavictor/portfolio/tree/main/google_tools) packages, these aren't meant to be deployed on other systems but rather provide insights into how I code/solve problems. Below is a breakdown of each script and what particular problem it was created to solve.
***
## update_payment.py

I was tasked with updating the primary payment method on roughly 9,000 Facebook ad accounts. Unfortunately there's no way to do this through the API, you <i>have</i> to manually do this directly in the Ads Manager UI. Considering how wasteful it would be to spend so much time on such a tedious task, I turned to Selenium and wrote this script to solve this issue.