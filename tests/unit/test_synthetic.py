from claims_intelligence.data.synthetic import generate_synthetic_data


def test_generator_is_reproducible_and_linked() -> None:
    first = generate_synthetic_data(200, 80, seed=7)
    second = generate_synthetic_data(200, 80, seed=7)
    assert first.claims.equals(second.claims)
    assert set(first.claims.policy_id).issubset(set(first.policies.policy_id))
    assert (first.claims.final_paid_amount > 0).all()
