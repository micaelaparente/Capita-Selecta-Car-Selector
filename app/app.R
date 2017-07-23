#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(readr)
library(dplyr)
tagged_op <- read_csv("tagged_op.csv")


categories = colnames(tagged_op[,-1])

ui <- fluidPage(
   

   titlePanel("Let's choose a car!"),
   
   sidebarLayout(
      sidebarPanel(
        uiOutput('resetable_input'),
        # checkboxGroupInput("car_tags",
        #              "Pick the most important characteristics you are looking for:",
        #              categories)
        
        actionButton("reset_input", "Reset inputs") ,
        p(),
        
        p("Developed by Micaela Parente. 
          Based on Edmunds user reviews of cars from 2016 and 2017.") ,
        
        tags$head(tags$style("p{color: #b3b3b3
                             }"
                         )
        )
       
      ),
      
      
      mainPanel(
         tableOutput("car_options")
      )
   )
)


server <- function(input, output) {
  
  result <- reactive({

    validate(
      need(input$car_tags != "", "")
    )
    
    filt_op = tagged_op[
      tagged_op[input$car_tags] %>% 
        mutate(filt = apply(.,1, prod) > 0.4) %>% select(filt) == TRUE,
      ]
    filt_op = filt_op %>%
      select(c("brand_model_year", input$car_tags))
    
    filt_op %>%
      mutate(filt = apply(filt_op[-1], 1, prod)) %>%
      arrange(desc(filt)) %>%
      select(brand_model_year) %>%
      rename(Suggestions = brand_model_year)
    
    
    }) 
   
  
  output$car_options <- renderTable({
     cars <- result()
     
     
   })
  
  output$resetable_input <- renderUI({
    times <- input$reset_input
    div(checkboxGroupInput("car_tags",
                           "Pick the most important characteristics you are looking for:",
                           categories))
  })
}

# Run the application 
shinyApp(ui = ui, server = server)

