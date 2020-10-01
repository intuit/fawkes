def generate_email(template_file_name, data):
    formatted_html = ""
    with open(template_file_name, "r") as template_file_handle:
        template_html = template_file_handle.read()
        for key in data:
            template_html = template_html.replace("${" + key + "}",
                                                  str(data[key]))
        formatted_html = template_html
    return formatted_html
