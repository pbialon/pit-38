import pendulum

LIST_OF_HOLIDAYS = [
    # todo: use https://www.geeksforgeeks.org/python-holidays-library/
    pendulum.parse(str_date) for str_date in [
        "2021-01-01",
        "2021-01-06",
        "2021-04-04",
        "2021-04-05",
        "2021-05-01",
        "2021-05-03",
        "2021-05-23",
        "2021-06-03",
        "2021-08-15",
        "2021-11-01",
        "2021-11-11",
        "2021-12-25",
        "2021-12-26",
    ]
]