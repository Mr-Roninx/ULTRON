import pytest
from synthetic_payment_universe.world_v12.entities.communication import Communication

def test_communication_entity_lifecycle():
    comm = Communication(
        communication_id="comm_1",
        customer_id="c_1",
        channel="WHATSAPP",
        template_id="payment_link_v1",
        sent_at=1760000000,
        delivered_at=1760000060,
        opened_at=1760000300,
        clicked_at=1760000450,
        converted=True
    )
    assert comm.channel == "WHATSAPP"
    assert comm.converted is True
    assert comm.clicked_at > comm.sent_at
