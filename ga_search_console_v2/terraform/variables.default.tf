variable "AWS_TAGS" {
  type = map(string)
  default = {
      "Project Name"        = "ga-search-console"
      "Project Description" = "This project implements a bot to call GA Search Console"
      "Sector"              = "Data Engineering"
      "Company"             = "company - company"
      "Cost center"         = "1010"
  }
}