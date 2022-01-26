library(scales)
library(ggplot2)
library(ggpubr)
require(tidyverse)
require(dplyr) 

#
# Global Functions
#
TryGetColumn <- function(x, column.name, value.if.not.exists = NA) {
  if (column.name %in% names(x)) {
    return(x[column.name])
  } 
  return(value.if.not.exists)
}



#
# Read Data
#
raw_result_data <- read.csv(file = 'Full_Results.csv')

number_of_papers = max(raw_result_data$Nummer)
number_of_criteria = 18


# -----------------------
# 3	:= Satisfies
# 2	:= Undocumented
# 1	:= Omit
# 0	:= N/A
# -----------------------

#
# General number across all papers and categories
#
all_results = raw_result_data %>% select(10:27)
occurences = table(unlist(all_results))
occurences_p = occurences / (number_of_papers * number_of_criteria)
paper_satisfie = occurences["3"] 
paper_satisfie_p = occurences_p["3"] 
paper_undocument = occurences["2"] 
paper_undocument_p = occurences_p["2"] 
paper_omit = occurences["1"] 
paper_omit_p = occurences_p["1"] 
paper_na = occurences["0"] 
paper_na_p = occurences_p["0"] 


#
# Get relative amount of papers for each category
#
category_data <- data.frame(Category=character(),
                 "0"=integer(), 
                 "1"=integer(), 
                 "2"=integer(),
                 "3"=integer(),
                 stringsAsFactors=FALSE) 
for(i in 10:ncol(raw_result_data)) {
  data = raw_result_data[,i]
  counts=round((table(data)/number_of_papers)*100, digit=0)
  
  new_data <- data.frame(paste("C", i-9), 
                         TryGetColumn(counts, "0"),TryGetColumn(counts, "1"),
                         TryGetColumn(counts, "2"),TryGetColumn(counts, "3"))
  names(new_data) <- c("Category", "0", "1", "2", "3")  
  category_data = rbind(category_data, new_data)
}
category_data[is.na(category_data)] <- 0
category_data
