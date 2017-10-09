# Gas Investments Dashboard

![Adventure time snail logo](https://vignette.wikia.nocookie.net/adventuretimewithfinnandjake/images/0/07/Waving_Snail.png/revision/latest?cb=20120729225549)

A dashboard to monitor and display investments. Incorporating shares and crypto currencies.
Benchmarking against market average returns and using data analysis tools to inform decisions.

### Feature List
 - [x] MongoDB provisioned
 - [x] Flask Web app created
 - [x] MongoEngine connection created
 - [x] Share historical data API connection
 - [x] DB model share schema
 - [x] DB model crypto schema
 - [x] WTF forms new share form
 - [x] WTF forms new crypto form
 - [ ] WTF update share form
 - [ ] WTF update share form
 - [x] Write historical data to DB
 - [x] Collate individual investment into single Pandas DF
 - [ ] Individual share page and graphs
 - [ ] Time Series dashboard total investments performance
    - [x] Compile share data total gains and losses and percentages
    - [x] Combine individual share data into single DataFrame
    - [x] Sum up daily values for total performance and investment per day
    - [x] Find S&P 500 data for time period
    - [x] Compare performance considering relevant fees for S&P buy ins 
        *Fees apply to individual share buys*
    - [x] Pass data to javascript file
    - [x] Add DC.js, D3.js and CrossFilter.js files
    - [x] Create time series chart of portfolio performance
 
 ### Quant Value Checklist
 *Gray, W, Carlisle, T (2013). Quantitative Value a practioners guide to automating intelligent investment and eliminating behavioral erros. NewJersey: Wiley Finance. p1-264.*
 
 
 #### 1. Identify Potential Fraud and Manipulation
 1.1 Accrual Screen
 
- [ ] *STA = Scaled Total Accruals = CA(t) - CL (t) - DEP(t)/ Total Assets(t)*

- [ ] *P_STA = Percentile(STA) among all firms in the universe*

- [ ] *SNOA = operating assets(t) - operating liabilities(t)/ total assets(t)*

- [ ] *P_SNOA = percentile(SNOA) among all firms in the universe*

- [ ] *COMBOACCRUAL = average(P_STA, P_SNOA)*

1.2 Fraud and Manipulation Screen

- [ ] *PROBM = -4.84 + 0.92 x DSRI + 0.528 x GMI + 0.404 x AQI + 0.892 x SGI + 0.115 x DEPI - 0.172 x SGAI + 4.679 x TATA - 0.327 x LVGI*
 
- [ ] *PMAN = CDF(PROBM)* 