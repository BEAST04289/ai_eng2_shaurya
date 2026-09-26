from src.business import theoretical_call_break_even_probability


def test_call_break_even_math():
    p = theoretical_call_break_even_probability()
    assert abs(p - (45 / (1150 * 0.35))) < 1e-12
    assert 0.11 < p < 0.12
