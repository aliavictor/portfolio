# Miscellaneous Scripts

This is a collection of various scripts that tackle specific obstacles I've encountered over the last couple years. Unlike the [facebook_tools](https://github.com/aliavictor/portfolio/tree/main/facebook_tools) and [google_tools](https://github.com/aliavictor/portfolio/tree/main/google_tools) packages, these aren't meant to be deployed on other systems but rather act as dummy scripts to provide insight into how I code/solve problems. Below is a breakdown of each script and what particular problem it was created to solve.
***
## update_payment.py

<b>Why this script was needed:</b> While the Facebook API is pretty robust, it does have its limitations and unfortunately that includes not being able to update payment methods. So when the primary payment method attached to an ad account needs to be updated, the <i>only</i> way to do this is to manually change the payment method directly in the Ads Manager UI. That's not so bad if you only have a handful of accounts, but if you have hundreds or thousands of accounts this definitely poses a problem.

<b>What this script does:</b> A browser is generated via Selenium/ChromeDriver and it's "taught" how to perform this task in the Ads Manager UI. The script then loops through each account in the queue and updates the payment method accordingly, being sure to keep track of how many attempts were made for each account. The queue is looped over 3 times to catch any instances where the update failed due to Ads Manager temporarily stalling.

## rss_parser_.py

This was a recent 2 hour exercise I did for another company. It presented an interesting
challenge and I had a lot of fun working through it, so I decided to include it.

For reference, I was given a normalized JSON file of RSS feed data from a slew of
articles across the web. The JSON may have been normalized, but just barely so; it was
still pretty messy in that not everything contained the same keys/information. The
challenge was as follows:

1. Determine which artist(s) each article is about
2. Match each artist to their corresponding database IDs using the company's public API
3. Return a JSON of this mapping