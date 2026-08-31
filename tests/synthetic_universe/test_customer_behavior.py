import pytest
from synthetic_payment_universe.schema.entities import Customer
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator

def test_customer_probabilistic_behavior():
    cust_fresh = Customer(customer_id="c_fresh", name="Fresh Corp", fatigue_score=0.10)
    cust_fatigued = Customer(customer_id="c_fatigued", name="Fatigued Corp", fatigue_score=0.85)

    # Fresh customer has higher link conversion than fatigued customer
    conversions_fresh = sum(CustomerGenerator.evaluate_link_conversion(cust_fresh, subseed=i) for i in range(100))
    conversions_fatigued = sum(CustomerGenerator.evaluate_link_conversion(cust_fatigued, subseed=i) for i in range(100))

    assert conversions_fresh > conversions_fatigued
