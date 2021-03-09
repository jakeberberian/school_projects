library(tidyverse)
library(randomForest)
library(shiny)
library(shinythemes)

nfl <- read_csv("data/nfl_play.csv") # Import data
nfl4 <- nfl %>%
  filter(play_type == "pass" & yards_gained < 35 | play_type == "run" & yards_gained < 15) %>%
  drop_na() 

# Teams relocate or abbreviation changes
nfl4$defteam <- gsub("STL", "LA", nfl4$defteam) #Rams 
nfl4$defteam <- gsub("LA" ,"LAR", nfl4$defteam)
nfl4$defteam <- gsub("JAC", "JAX", nfl4$defteam) #Jaguars
nfl4$defteam <- gsub("SD", "LAC", nfl4$defteam) #Chargers

# Change side_of_field to "own" or "opposing"
nfl5 <- nfl4 %>%
  mutate(side_of_field = case_when(defteam == side_of_field ~ "opposing",
                                   TRUE ~ "own"))

nfl5$play_type<-as.factor(nfl5$play_type) # Convert play_type to factor
nfl5$side_of_field<-as.factor(nfl5$side_of_field) # Convert side_of_field to factor
nfl5$defteam<-as.factor(nfl5$defteam) # Convert defteam to factor

# Teams relocate or abbreviation changes
nfl4$defteam <- gsub("STL", "LA", nfl5$defteam) #Rams 
nfl4$defteam <- gsub("LA" ,"LAR", nfl5$defteam)
nfl4$defteam <- gsub("JAC", "JAX", nfl5$defteam) #Jaguars
nfl4$defteam <- gsub("SD", "LAC", nfl5$defteam) #Chargers

# Split data into run and pass data frames
run <- nfl5 %>%
  filter(play_type == "run")

pass <- nfl5 %>%
  filter(play_type == "pass")

rm(nfl4)

rf_pass <- randomForest(yards_gained ~ . -play_type, data = pass, ntree = 40)
rf_run <- randomForest(yards_gained ~ . -play_type, data = run, ntree = 40)


############ Shiny

ui <- fluidPage(
  titlePanel("Yard Predictor"),
  
  theme = shinytheme("slate"),
  
  tags$style(HTML("
                    .dataTables_wrapper .dataTables_length, .dataTables_wrapper .dataTables_filter, .dataTables_wrapper .dataTables_info, .dataTables_wrapper .dataTables_processing, .dataTables_wrapper .dataTables_paginate, .dataTables_wrapper .dataTables_paginate .paginate_button.current:hover {
                    color: #ffffff;
                    }
### ADD THIS HERE ###
                    .dataTables_wrapper .dataTables_paginate .paginate_button{box-sizing:border-box;display:inline-block;min-width:1.5em;padding:0.5em 1em;margin-left:2px;text-align:center;text-decoration:none !important;cursor:pointer;*cursor:hand;color:#ffffff !important;border:1px solid transparent;border-radius:2px}

###To change text and background color of the `Select` box ###
                    .dataTables_length select {
                           color: #0E334A;
                           background-color: #0E334A
                           }

###To change text and background color of the `Search` box ###
                    .dataTables_filter input {
                            color: #0E334A;
                            background-color: #0E334A
                           }

                    thead {
                    color: #ffffff;
                    }

                     tbody {
                    color: #000000;
                    }

                   "
                  
                  
  )),

  
  sidebarLayout(
    sidebarPanel(
      selectInput("down",
                  label = "Select a down",
                  choices = list("First" = 1, "Second" = 2, "Third" = 3, "Fourth" = 4)
      ),
      
      sliderInput("ydstogo",
                  label = "Yards to first down",
                  min = 0, max = 100,
                  value = 5
      ),
      
      selectInput("play_type",
                  label = "Pass or Run?",
                  choices = list("Pass" = "pass", "Run" = "run")
      ),
      
      radioButtons("side_of_field",
                   label = "Side of Field",
                   choices = list("Own" = "own", "Opposing" = "opposing")
      ),
      
      selectInput("defteam",
                  label = "Defending Team",
                  choices = list(
                    "Arizona Cardinals" = "ARI",
                    "Atlanta Falcons" = "ATL",
                    "Baltimore Ravens" = "BAL",
                    "Buffalo Bills" = "BUF",
                    "Carolina Panthers" = "CAR",
                    "Chicago Bears" = "CHI",
                    "Cincinnati Bengals" =  "CIN",
                    "Cleveland Browns" = "CLE",
                    "Dallas Cowboys" = "DAL",
                    "Denver Broncos" = "DEN",
                    "Detroit Lions" = "DET",
                    "Green Bay Packers"  = "GB", 
                    "Houston Texans" = "HOU",
                    "Indianapolis Colts" = "IND",
                    "Jacksonville Jaguars" = "JAX",
                    "Kansas City Chiefs" = "KC",
                    "Los Angeles Rams" = "LAR",
                    "Los Angeles Chargers" = "LAC", 
                    "Miami Dolphins" = "MIA",
                    "Minnesota Vikings" = "MIN",
                    "New England Patriots" = "NE",
                    "New Orleans Saints" = "NO",
                    "New York Giants" = "NYG",
                    "New York Jets" = "NYJ",
                    "Oakland Raiders" = "OAK",
                    "Philadelphia Eagles" = "PHI",
                    "Pittsburgh Steelers" = "PIT",
                    "Seattle Seahawks" = "SEA",
                    "San Francisco 49ers" = "SF",
                    "Tampa Bay Buccaneers" = "TB",
                    "Tennessee Titans" = "TEN",
                    "Washington Redskins" = "WAS")
      ),
      
      submitButton("Submit")
      
    ),
    
    # mainPanel(
    #   textOutput("yards")
    # ), 
    
    mainPanel(
      
      tabsetPanel(type = "tabs",
                  
                  tabPanel("Yardage Predictor", verbatimTextOutput("yards")), # Regression output
                  tabPanel("Data", DT::dataTableOutput('tbl')) # Data as datatable
                  
      )
    )
  
))


server<-function(input, output) {
  
  output$yards<-renderText({
    inputs<-function(d, pt, ytg, sof, dt) {
      df_levels<-levels(nfl5$defteam)
      
      df<-as.data.frame(matrix(data = NA, ncol = 5))
      colnames(df)<-c("down", "play_type", "ydstogo", "side_of_field", "defteam")
      df$down<-input$down
      df$play_type<-factor(input$play_type, levels = c("pass", "run"))
      df$ydstogo<-input$ydstogo
      df$side_of_field<-factor(input$side_of_field, levels = c("own", "opposing"))
      df$defteam<-factor(input$defteam, levels = df_levels)
      
      return(df)
    }
    
    test <- inputs(3, "run", 15, "own", "TEN")
    
    pred_yds<-if (test$play_type=="pass") { 
      predict(rf_pass, test)
    } else if (test$play_type=="run") {
      predict(rf_run, test)
    }
    
    print(paste("By choosing to ", input$play_type, ", you can expect to gain ", round(pred_yds, 1), " yards.", sep = ""))
  })
  
  
  
  output$tbl = DT::renderDataTable({
    DT::datatable(nfl5, options = list(lengthChange = FALSE))
  })
}

shinyApp(ui, server)
