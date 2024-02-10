variable "AWS_TAGS" {
  type = map(string)
  default = {
      "Project Name"        = "ga-analytics-service"
      "Project Description" = "This project implements a bot to call GA4 AnalyticsService"
      "Sector"              = "Data Engineering"
      "Company"             = "company - company"
      "Cost center"         = "1010"
  }
}