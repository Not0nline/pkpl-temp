import datetime
from unittest import TestCase
import pytest
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from reksadana_rest.models import (
    Bank, CategoryReksadana, Reksadana,
    HistoryReksadana, UnitDibeli
)
import uuid


@pytest.fixture
def sample_data(db):
    bank1 = Bank.objects.create(name="Bank A")
    bank2 = Bank.objects.create(name="Bank B")
    category = CategoryReksadana.objects.create(name="Pasar Uang")

    reksadana = Reksadana.objects.create(
        name="Reksa Dana Ajaib",
        category=category,
        kustodian=bank1,
        penampung=bank2,
        nav=1000,
        aum=100000,
        tingkat_resiko="Moderat"
    )
    return {
        "reksadana": reksadana,
        "bank1": bank1,
        "bank2": bank2,
        "category": category
    }


def test_bank_model(sample_data):
    assert Bank.objects.count() == 2


def test_category_model(sample_data):
    assert CategoryReksadana.objects.count() == 1


def test_reksadana_model_fields(sample_data):
    reksadana = sample_data["reksadana"]
    assert reksadana.name == "Reksa Dana Ajaib"
    assert reksadana.nav == 1000
    assert reksadana.aum == 100000


def test_generate_history_when_none_exists(sample_data):
    reksadana = sample_data["reksadana"]
    assert HistoryReksadana.objects.count() == 0
    reksadana.generate_made_up_history_per_hour()
    assert HistoryReksadana.objects.count() == 1

def test_generate_hourly_history(sample_data):
    reksadana = sample_data["reksadana"]
    # Create initial history 5 hours ago
    initial_time = datetime.datetime.now() - timedelta(hours=5)
    assert timezone.is_naive(initial_time)
    HistoryReksadana.objects.create(
        id_reksadana=reksadana,
        date=initial_time,
        nav=1000,
        aum=100000
    )
    assert HistoryReksadana.objects.count() == 1

    # Generate history for 5 missing hours
    reksadana.generate_made_up_history_per_hour()
    assert HistoryReksadana.objects.count() == 6  # 1 original + 5 new


def test_generate_history_no_new_data_needed(sample_data):
    reksadana = sample_data["reksadana"]
    now = datetime.datetime.now()
    HistoryReksadana.objects.create(
        id_reksadana=reksadana,
        date=now,
        nav=1000,
        aum=100000
    )
    reksadana.generate_made_up_history_per_hour()
    assert len(HistoryReksadana.objects.filter(id_reksadana=reksadana)) == 1  # No new data needed


def test_unit_dibeli_valid(sample_data):
    reksadana = sample_data["reksadana"]
    unit = UnitDibeli.objects.create(
        user_id=uuid.uuid4(),
        id_reksadana=reksadana,
        nominal=50000,
        waktu_pembelian=timezone.now(),
        nav_dibeli=1050
    )
    assert unit.nominal == 50000


def test_unit_dibeli_invalid_nominal(sample_data):
    reksadana = sample_data["reksadana"]
    unit = UnitDibeli(
        user_id=uuid.uuid4(),
        id_reksadana=reksadana,
        nominal=-100,
        waktu_pembelian=timezone.now(),
        nav_dibeli=900
    )
    with pytest.raises(ValueError, match="Ini apaan uang <0 :V"):
        unit.clean()

