# Stockfeels
This is a light-hearted web app that will keep track of the feelings you have during stock trades. After registering and logging in, users will be able to create journal entries about their stock transactions.

When looking at their own entries, users can obtain the current stock price of the stock that they trades, and compare it to the trade that they made. 


### Technical Details
The backend of this app is written in python 3.7 and uses the Flask framework. User authentication info and journal entry details are stored in a SQLite database. 

Current stock prices are obtained using the IEX API.

The frontend is styled with Bootstrap but currently uses no other frameworks or libraries.
