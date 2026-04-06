from src.rule_engine import get_quote

# Age 18-39
def test_age_18_39_high_bmi():
    assert get_quote({"age": 25, "bmi": 38, "gender": "Male"})["quote"] == 800

def test_age_18_39_low_bmi():
    assert get_quote({"age": 25, "bmi": 16, "gender": "Male"})["quote"] == 800

def test_age_18_39_normal_bmi():
    assert get_quote({"age": 25, "bmi": 25, "gender": "Male"})["quote"] == 600

# Age 40-59
def test_age_40_59_high_bmi():
    assert get_quote({"age": 50, "bmi": 38, "gender": "Male"})["quote"] == 900

def test_age_40_59_low_bmi():
    assert get_quote({"age": 50, "bmi": 17, "gender": "Male"})["quote"] == 900

def test_age_40_59_normal_bmi():
    assert get_quote({"age": 50, "bmi": 25, "gender": "Male"})["quote"] == 600

# Age 60+
def test_age_over_60_high_bmi():
    assert get_quote({"age": 65, "bmi": 45, "gender": "Male"})["quote"] == 18000

def test_age_over_60_low_bmi():
    assert get_quote({"age": 65, "bmi": 17, "gender": "Male"})["quote"] == 18000

def test_age_over_60_normal_bmi():
    assert get_quote({"age": 65, "bmi": 25, "gender": "Male"})["quote"] == 600

# Female discount
def test_female_discount():
    result = get_quote({"age": 30, "bmi": 25, "gender": "Female"})
    assert result["quote"] == 540
    assert "10% discount" in result["reason"]

def test_female_discount_high_risk():
    result = get_quote({"age": 25, "bmi": 38, "gender": "Female"})
    assert result["quote"] == 720

# Boundaries
def test_age_boundary_60():
    assert get_quote({"age": 60, "bmi": 38, "gender": "Male"})["quote"] == 600

def test_bmi_boundary_37_5():
    assert get_quote({"age": 25, "bmi": 37.5, "gender": "Male"})["quote"] == 600

def test_bmi_boundary_17():
    assert get_quote({"age": 25, "bmi": 17, "gender": "Male"})["quote"] == 600
