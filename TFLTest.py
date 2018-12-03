from TFL import BikeScrape

bs = BikeScrape()

bs.scrape(10)
bs.createDFs()
bs.writeToCSV("test_")
