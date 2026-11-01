from common import *


def test(driver):
    login(driver, VALID_USER, VALID_PASS)
    try:
        WebDriverWait(driver, 15).until(
            EC.invisibility_of_element_located(PASSWORD_BOX)
        )
        return True, "User logged in successfully and navigated to dashboard"
    except TimeoutException:
        return False, "Still on login page after entering valid credentials"


run_test("COR-TC001", test)