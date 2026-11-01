from common import *


def test(driver):
    login(driver, INVALID_USER, INVALID_PASS)
    try:
        msg = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(ERROR_MSG)
        ).text
        return True, f"Error message displayed: {msg}"
    except TimeoutException:
        return False, "No error message displayed for invalid login"


run_test("COR-TC002", test)