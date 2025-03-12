from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..models.books import Roll, RollCreate, RollResponse
from datetime import datetime, timedelta
from ..database import SessionLocal
from typing import Optional
from collections import defaultdict


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/rolls/', response_model=RollResponse)
def create_roll(roll: RollCreate, db: Session = Depends(get_db)):
    db_roll = Roll(**roll.dict())
    db.add(db_roll)
    db.commit()
    db.refresh(db_roll)
    return db_roll


@router.delete('/rolls/{roll_id}', response_model=RollResponse)
def delete_roll(roll_id: int, db: Session = Depends(get_db)):
    db_roll = db.query(Roll).filter(Roll.id == roll_id).first()
    if not db_roll:
        raise HTTPException(status_code=404, detail='Roll not found')
    db_roll.removed_date = datetime.utcnow()
    db.commit()
    db.refresh(db_roll)
    return db_roll


@router.get('/rolls/', response_model=list[RollResponse])
def get_rolls(
    id_range: Optional[str] = Query(None, description='Фильтр по диапазону id (например, \'1-10\')'),
    weight_range: Optional[str] = Query(None, description='Фильтр по диапазону веса (например, \'100-200\')'),
    length_range: Optional[str] = Query(None, description='Фильтр по диапазону длины (например, \'5-15\')'),
    added_date_range: Optional[str] = Query(None,
                                            description='Фильтр по диапазону даты добавления'
                                                        '(например, \'2023-01-01-2023-12-31\')'),
    removed_date_range: Optional[str] = Query(None,
                                              description='Фильтр по диапазону даты удаления'
                                                          '(например, \'2023-01-01-2023-12-31\')'),
    db: Session = Depends(get_db)
):
    query = db.query(Roll)

    if id_range:
        start, end = map(int, id_range.split('-'))
        query = query.filter(Roll.id >= start, Roll.id <= end)

    if weight_range:
        start, end = map(float, weight_range.split('-'))
        query = query.filter(Roll.weight >= start, Roll.weight <= end)

    if length_range:
        start, end = map(float, length_range.split('-'))
        query = query.filter(Roll.length >= start, Roll.length <= end)

    if added_date_range:
        start, end = map(lambda x: datetime.strptime(x, '%Y-%m-%d'), added_date_range.split('-'))
        query = query.filter(Roll.added_date >= start, Roll.added_date <= end)

    if removed_date_range:
        start, end = map(lambda x: datetime.strptime(x, '%Y-%m-%d'), removed_date_range.split('-'))
        query = query.filter(Roll.removed_date >= start, Roll.removed_date <= end)

    return query.all()


@router.get('/rolls/stats/')
def get_stats(start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):
    rolls = db.query(Roll).filter(Roll.added_date >= start_date, Roll.removed_date <= end_date).all()
    if not rolls:
        raise HTTPException(status_code=404, detail='No rolls found in this period')

    daily_counts = defaultdict(int)
    daily_weights = defaultdict(float)

    for roll in rolls:
        current_date = roll.added_date
        while current_date <= (roll.removed_date or datetime.utcnow()):
            daily_counts[current_date.strftime("%Y-%m-%d")] += 1
            daily_weights[current_date.strftime("%Y-%m-%d")] += roll.weight
            current_date += timedelta(days=1)

    min_count_day = min(daily_counts, key=daily_counts.get)
    max_count_day = max(daily_counts, key=daily_counts.get)

    min_weight_day = min(daily_weights, key=daily_weights.get)
    max_weight_day = max(daily_weights, key=daily_weights.get)

    stats = {
        'added_count': len([r for r in rolls if r.added_date >= start_date]),
        'removed_count': len([r for r in rolls if r.removed_date <= end_date]),
        'avg_length': sum(r.length for r in rolls) / len(rolls),
        'avg_weight': sum(r.weight for r in rolls) / len(rolls),
        'max_length': max(r.length for r in rolls),
        'min_length': min(r.length for r in rolls),
        'max_weight': max(r.weight for r in rolls),
        'min_weight': min(r.weight for r in rolls),
        'total_weight': sum(r.weight for r in rolls),
        'max_duration': max((r.removed_date - r.added_date).days for r in rolls if r.removed_date),
        'min_duration': min((r.removed_date - r.added_date).days for r in rolls if r.removed_date),
    }
    return stats
