# Facebook Tools

Utilities for the Facebook Marketing API. For any questions/comments, please email alia.jo.victor@gmail.com.

## FACEBOOK class

The user will need a [user access token](https://developers.facebook.com/docs/facebook-login/access-tokens/?locale=en_US) in order to use this class. Please reference [Facebook's Marketing API guide](https://developers.facebook.com/docs/marketing-api/reference/) to see what fields/parameters are available for the kind of objects you're working with.

### read function

Performs a single `GET` request via Facebook's Graph API and returns the JSON response. The parameters include:<br>
- <b>obj_id:</b> ID of a Facebook marketing object (i.e. an adset ID)<br>
	- <b>Note:</b> If you pass an account ID, you must prefix the ID with <b>act_</b><br>
- <b>edge (optional):</b> The edge you'd like to access for the given object (i.e. insights)<br>
- <b>fields:</b> A list of fields you want to include in the `GET` request<br>
- <b>only_url (boolean):</b> When this is set to True, no `GET` request is made but the compiled graph API url for the request is instead returned<br>
- <b>params (optional):</b> Dictionary of available parameters for the given object<br>
	- For example, this would give you insights data for adset 123456 from just the past week: `read('123456',edge='insights',fields=['spend','inline_link_clicks'],**{'date_preset':'last_7d'})`

### bulk_read function

As its name suggests, this is essentially the same as the `read` function but it's designed for multiple `GET` requests (and has no only_url parameter). By utilizing `asyncio` and `aiohttp` thousands of requests can be performed asynchronously. Instead of a single ID, a list of IDs for marketing objects are passed. Like the `read` function, when working with ad accounts remember each ID in your list must have the <b>act_</b> prefix.<br>

## Prerequisites<br>
- pandas
- requests
- asyncio
- nest_asyncio
- aiohttp
- functools
- datetime
