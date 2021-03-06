# Alia's Toolbox

This is a collection of various little helper tools I've built over the years. They're not particularly fancy, it just allows you to use less code so things are more concise and easier to read. For example, `reset(df)` is the equivalent of `df.reset_index(drop=True)`. The former artist in me loves colors, so on top of building practical helper functions there are also various aesthetic helper functions as well. 
***
### helpers.py

These consist of the practical/functional helper tools. They encompass pretty much everything; dataframes, calculations, text, etc.

### colors.py

These are purely for aesthetic purposes, mostly consisting of functions that print in particular colors. Printing certain information in particular colors (i.e. printing errors/warnings in <font color="red">red</font>) is helpful on its own, but these functions take it a step further and allow you to use (basic) HTML text formatting for further visual cues. For example, `red('This is a big error!',False)` would print "<font color="red">This is a big error!</font>" in red text. Similarly `red('This is a <b>big</b> error!',False)` would print "<font color="red">This is a <b>big</b> error!</font>" in red text as well, but with big bolded this time.