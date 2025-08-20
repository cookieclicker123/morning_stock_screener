every morning, i want to wake up and recieve the top 10 stocks that are most likely to go up in the day and the near to medium term future. this is simply it. I want to know this such that i can buy them and sell them at the right time.

i primiarly trade options, and only on us stocks. 

by reciecing this informaiton at 9:30am BST every day, i will be able to get a top ten list sent to my email via smtp integration.

the email begins with general market conditions and macroeconomic news that would be noteworthy to a trader as i can indirectly infer the best picks from this.

then we have the list of stocks, with the following information:

- stock name
- stock symbol
- stock price
- stock change
- stock change percentage
- stock volume
- stock market cap
- stock industry
- detailed fundamental analysis
- detailed technical analysis
- detailed news analysis
- detailed analyst recommendations
- detailed analyst price targets
- detailed sudden news, innvoative products, regulatory approvals, etc.

the amulgum of essentially all the current informaiton about the market and detailed analysis of each of the stocks will allow a final synthesis agent to determine the rankings based on all the factors analysed and condense the market into a top 10 list everyday.

Each stock should have a summary seciton of why it serves as a prudent short term play, and then detailed analysis of why it is a good long term play according to the checklist above.

as of now , we will achieve this through integraiton with the following services:

Yahoo Finance

CNBC

Bloomberg

MarketWatch

Reuters

Financial Times

Forbes

Wall Street Journal

CNN Money

Stock Analysis (stockanalysis.com)

WallStreetZen

Finbox

SimplyWall.St

Investing.com

TradingView

Morningstar

MarketBeat

The Motley Fool

Seeking Alpha

Reddit (r/stocks, r/ValueInvesting)

TheStreet

Investopedia

Google Finance

we will do this by using the following tools:

- python
- gpt5
- custom agent framework:
primary: orcheastrator
secondary: 1) market analysis and macroeconomic analysis. 2) stock analysis. 3) news analysis. 4) ranker agent 5) synthesis agent 6) email sender agent

the orcheastrator will be used to orchaestrate the other agents to work together, following a rigorous nested set of instrucitons and a set of rules. we want reliable and consistent outputs after all from the llm.

the tools used to achieve this to keep it brief will be google serper . use the one thats the fastest.
i think we can use this by defining a very rigorous list of preliminary searches and then using the results to feed into the next search by making augmented google friendly searches with ai after it has been fed the preliminary results, and created a market scan.

the preliminary analysis phase is crucial, it must be so rigorous that we remove the possible that the system is medicore because of low recall. often the best oppurtunities are early ones not making massive noise, but somewhere on the web clues point to stocks that present great near term and long term oppurtunity and coupled with market conditions etc and a massive synthesis of other factors present a nuanced case that the system needs to throughly search through the recesses of the internet for. serper is fast, and this will eventually be a cron job anyway, as long as it arrives as an email at 9:30am everyday, it doesnt necessarily need to be the absolute fastest process, it must be focused on not 'missing' an oppurtunity that the trader otherwise would have taken.

therefore for traders who have deep technical skill, often their main problem is simply waking up every day and spedning hours to find the oppurtunities , when they could be using their time to just do their own deeper analuysis, freeing them of the research burden to a large degree.

therefore fundemtnally we will use gpt5, and google serper for now to create an advanced top 10 stocks now list for email. the details can be figured out carefully by us working together.

we will not get ahead of oursevles and must use test driven devleopment to iteratively add features.

we will enscone the project in uv and pyproject.toml. we will need a serper api key and then an openai api key. hopefully for now that is sufficient, remember i will improve the system once its built vastly. for now we just need to prove it can be made.

its important to focus on good system design and build slowly but precisely.

therefore you will first build the pydantic data models, and only add dependencies to the uv virtual env as we need them, we will build file by file and not rush.

the first thing we will do is build an abstracted llm wrapper around gpt5 that uses our api contracts to accept a query and return a response. eventually we will build models for the input being the system prompt augmented with the preliminary results and then the final results from serper, but tnone of that matters now and the system should be built first as if it is a simple llm wrapper with a simple chat app for me to test with. make sure to build proper folder strcutures for all of this so we design professionally and focus on good abstracted functions that are stateless , built on robust api data strcutures only, and use the best practices for the language.

every package chosen must be evaluated against other options and be seen as rhe best choice for the job. you will ask yourself this quesiton many times and we want to be careful about adding bloat we dont need.

you will build the funcitonal business components of the system with isloated tests and exmaples proving they work.

you will let me build prompts, and inputs to serper in long run . but that isnt relavent yet unless we are at this stage of dev. in early stages we use simple one generated by you and simply searches accroding to the criteria generated by you.

this should be enough info for now.

focus on getting the skeleton of the project ready, and making everyhting intutivie and easy to run including tests , exmaples, and documentation. you can use a makefile for this and uv and make sure how to use them is clear in the empty readme.md. keep that file concise, containg only the setup for the project as well as the tests and exmaples and eventually app.

make sure you do notn get ahead of yourself and build out things we dont need yet.
