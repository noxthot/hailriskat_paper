import inquirer


def ask_model_cfg():
    questions = [
        inquirer.List(
            'target',
            message="Give the kernel size for maxpooling. Should be a positive integer",
            choices=[
                        'data_mehs_orig',
                        'data_mehs_maxpool3',
                        'data_mehs_maxpool5',
                        'data_mehs_maxpool7',
                        'data_mehs_maxpool9',
                        'data_mehs_maxpool11',
                        'data_mehs_max_preserving_gausspool3',
                        'data_mehs_max_preserving_gausspool5',
                        'data_mehs_max_preserving_gausspool7',
                        'data_mehs_max_preserving_gausspool9',
                        'data_mehs_max_preserving_gausspool11',
                        'data_mehs_max_preserving_meanpool3',
                        'data_mehs_max_preserving_meanpool5',
                        'data_mehs_max_preserving_meanpool7',
                        'data_mehs_max_preserving_meanpool9',
                        'data_mehs_max_preserving_meanpool11',
                        'data_mehs_max_preserving_medianpool3',
                        'data_mehs_max_preserving_medianpool5',
                        'data_mehs_max_preserving_medianpool7',
                        'data_mehs_max_preserving_medianpool9',
                        'data_mehs_max_preserving_medianpool11',
                        'data_mehs_max_preserving_90percentilepool3',
                        'data_mehs_max_preserving_90percentilepool5',
                        'data_mehs_max_preserving_90percentilepool7',
                        'data_mehs_max_preserving_90percentilepool9',
                        'data_mehs_max_preserving_90percentilepool11',
                        'data_mehs2poh',
            ]
        ),
        inquirer.Text(
            'threshold',
            message="Exclude ares with less than ... observations",
        ),
        inquirer.Checkbox(
            'return_periods',
            message="Choose the desired return periods.",
            choices=([2, 3] + list(range(5, 101, 5))),
            default=[2, 5, 10, 20, 25, 30, 50, 100],
        ),
        inquirer.List(
            'distribution',
            message="Choose the underlying distribution assumption",
            choices=["weibull", "lognorm"],
        ),
        inquirer.List('method',
                            message="Which optimization method should be used?",
                            choices=[
                                        "MLE",
                                        "PWM"
                                    ]
                            )
    ]
    answers = inquirer.prompt(questions)

    target = answers["target"]
    threshold = int(answers["threshold"])
    return_periods = answers["return_periods"]
    distribution = answers["distribution"]
    method = answers["method"]

    config_model = dict()
    config_model["target"] = target
    config_model["threshold"] = threshold
    config_model["return_periods"] = return_periods
    config_model["distribution"] = distribution
    config_model["method"] = method

    return config_model
