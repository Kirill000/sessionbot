from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, Text, DateTime, Boolean, ForeignKey
from models import Users, SAU, Schemotech
from sqlalchemy.orm import Session

metadata = MetaData()
engine = create_engine("postgresql+psycopg2://postgres:admin@localhost:5432/spbot", future=True)  

shm_questions = [
"1. Классификация усилителей.",
"2. Основные технические показатели усилителей.",
"3. Характеристики усилителей и их взаимосвязь.",
"4. Эквивалентная схема замещения биполярного транзистора.",
"5. Эквивалентная схема замещения полевого транзистора.",
"6. Усилительный каскад с ОЭ. Динамические характеристики.",
"7. Эквивалентная схема замещения каскада с ОЭ для средних частот. ",
"8. Эквивалентная схема замещения каскада с ОЭ для высоких частот. ",
"9. Эквивалентная схема замещения каскада с ОЭ для низких частот. ",
"10. Каскад с ОБ. Эквивалентная схема замещения.",
"11. Каскад с ОБ. Эквивалентная схема замещения для средних частот. ",
"12. Каскад с ОБ. Эквивалентная схема замещения для высоких частот. ",
"13. Каскад с ОБ. Эквивалентная схема замещения для низких частот. ",
"14. Каскад с ОК. Эквивалентная схема замещения.",
"15. Каскад с ОК. Эквивалентная схема замещения для средних частот. ",
"16. Каскад с ОК. Эквивалентная схема замещения для низких частот. ",
"17. Каскад с ОК. Эквивалентная схема замещения для высоких частот.",
"18. Сравнительная оценка различных схем включения биполярного транзистора. ",
"19. Каскад с ОИ. Эквивалентная схема замещения.",
"20. Каскад с ОИ. Эквивалентная схема замещения для средних частот. ",
"21. Каскад с ОИ. Эквивалентная схема замещения для низких частот.",
"22. Каскад с ОИ. Эквивалентная схема замещения для высоких частот. ",
"23. Каскад с ОС. Эквивалентная схема замещения.",
"24. Каскад с ОС. Эквивалентная схема замещения для средних частот. ",
"25. Каскад с ОС. Эквивалентная схема замещения для высоких частот. ",
"26. Каскад с ОС. Эквивалентная схема замещения для низких частот. ",
"27. Сравнительная оценка различных схем включения полевого транзистора. ",
"28. Усилители с обратной связью. Общие сведения. Виды ОС.",
"29. Влияние обратной связи на характеристики усилителя (стабильность коэффициента усиления, нелинейные искажения).",
"30. Влияние последовательной обратной связи по напряжению на входное сопротивление усилителя.",
"31. Влияние последовательной обратной связи по напряжению на выходное сопротивление усилителя.",
"32. Влияние параллельной обратной связи по току на входное сопротивление усилителя.",
"33. Влияние параллельной обратной связи по току на выходное сопротивление усилителя.",
"34. Влияние отрицательной обратной связи на частотную характеристику усилителя. ",
"35. Усилители мощности. Классификация усилителей мощности.",
"36. Усилитель мощности в режиме А.",
"37. Усилитель мощности в режиме АВ. ",
"38. Усилитель мощности в режиме В. ",
"39. Усилитель мощности в режиме С. ",
"40. Усилитель мощности в режиме D. ",
"41. Однотактные усилители мощности.",
"42. Двухтактные усилители мощности.",
"43. Бестрансформаторные усилители мощности.",
"44. Фазоинверсные схемы в усилителях мощности.",
"45. Токовые бустеры.",
"46. Усилители постоянного тока. Основные сведения. Мостовая схема включения источника сигнала и нагрузки.",
"47. Двухкаскадный усилитель постоянного тока.",
"48. Усилитель постоянного тока с преобразованием сигнала.",
"49. Дифференциальный усилитель.",
"50. Схемы включения дифференциального усилителя.",
"51. Точностные параметры дифференциального усилителя",
"52. Операционный усилитель. Основные сведения, обозначение",
"53. Структурная схема ОУ. Упрощенная электрическая схема ОУ Основные параметры ОУ",
"54. Корекция частотной характеристов ОУ. Точностные параметры ОУ ",
"55. Улучшение параметров ОУ",
"56. Основные схемы включения ОУ",
"57 Операционные усилители с однополярным питанием. Линейные аналоговые схемы на ОУ",
"58 Активные электрические фильтры. Фазовые фильтры",
"59. Измерительные усилители: назначение и основные виды",
"60. Покажите принцип действия и приведите выходные статические характеристики п-р-n биполярного транзистора.",
"61. Приведите основные схемы включения транзистора.",
"62. Чем отличаются выходные ВАХ транзистора, включенного по схеме ОЭ и ОБ? ",
"63. Приведите сравнительный анализ схем включения биполярного транзистора. ",
"64. Схемотехника операционных усилителей. Входные каскады",
"65. Схемотехника операционных усилителей. Выходные каскады",
"66. Передаточная функция операционных усилителей с обратными связями. Частотно независимые и частотно зависимые обратные связи. Частотная, фазовая, амплитудная и импульсная характеристики операционных усилителей",
"67. Схемотехника операционных усилителей с обратной связью: инвертирующее включение",
"68. Схемотехника операционных усилителей с обратной связью: не инвертирующее включение",
"69. Схемотехника операционных усилителей с обратной связью: суммирующий инвертирующий усилитель",
"70. Схемотехника операционных усилителей с обратной связью: суммирующий не инвертирующий усилитель",
"71. Схемотехника операционных усилителей с обратной связью: суммирующе дифференциальный усилитель",
"72. Схемотехника операционных усилителей с обратной связью: инвертирующий интегрирующий усилитель",
"73. Схемотехника операционных усилителей с обратной связью: не инвертирующий интерирующий усилитель",
"74. Схемотехника операционных усилителей с обратной связью: инвертирующий дифференцирующий усилитель",
"75. Схемотехника операционных усилителей с обратной связью: не инвертирующий дифференцирующий усилитель",
"76. Схемотехника операционных усилителей с обратной связью: двойной интегрирующий усилитель",
"77. Схемотехника операционных усилителей с обратной связью: полосовой фильтр на операционном усилителе",
"78. Схемотехника операционных усилителей с обратной связью; компаратор напряжения",
"79. Схемотехника операционных усилителей с обратной связью: генератор гармонических сигналов",
"80. Схемотехника операционных усилителей с обратной связью: инструментальные усилители"
]

users = Table('users', metadata,
    Column("id", Integer),  # Уникальный идентификатор   
    Column("user_created", DateTime, default=datetime.now()),      # Дата и время создания
    Column("subjects_allowed_to_read", String, nullable=False, default=''),
    Column("is_banned", Boolean, nullable=False, default=False),
    Column("is_admin", Boolean, nullable=False, default=False),
)

sau = Table('sau', metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),  # Уникальный идентификатор
    Column("title", String, nullable=False),
    Column("answer_text", String, nullable=True, default=None),
    Column("answer_imgs", String, nullable=True, default='[]'),
    Column("author", Integer, nullable=True),
    Column("is_empty", Boolean, default=True),
    Column("is_approved", Boolean, default=False)
)

schemotech = Table('schemotech', metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),  # Уникальный идентификатор
    Column("title", String, nullable=False),
    Column("answer_text", String, nullable=True, default=None),
    Column("answer_imgs", String, nullable=True, default='[]'),
    Column("author", Integer, nullable=True),
    Column("is_empty", Boolean, default=True),
    Column("is_approved", Boolean, default=False)
)

metadata.create_all(engine)
with Session(autoflush=False, bind=engine) as db:
    id_ = 0
    for q in shm_questions:
        s1 = Schemotech(id=id_, title=q[3:])
        db.add(s1)
        id_ += 1
    db.commit()
