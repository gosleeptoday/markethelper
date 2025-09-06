from tortoise import fields
from tortoise.models import Model


class Tariff(Model):
    """
    Тарифы подписки (например: Индивидуал, Складчина).
    """
    id = fields.IntField(pk=True)      # 1,2,...
    code = fields.CharField(50, unique=True)  # "INDIVIDUAL", "GROUP"
    name = fields.CharField(100)       # Читаемое имя

    class Meta:
        table = "tariffs"


class Status(Model):
    """
    Универсальная таблица для всех статусов.
    Например:
      type = "subscription", code = "ACTIVE", name = "Активна"
      type = "subscription", code = "EXPIRED", name = "Истекла"
      type = "request", code = "PENDING", name = "В ожидании"
    """
    id = fields.IntField(pk=True)
    type = fields.CharField(50, index=True)   # категория статуса ("subscription","request","file_update","ai_rating")
    code = fields.CharField(50)               # машинное имя
    name = fields.CharField(100)              # человеко-читаемое имя

    class Meta:
        table = "statuses"
        unique_together = (("type", "code"),)


class Duration(Model):
    """
    Длительности подписок (в месяцах).
    """
    id = fields.IntField(pk=True)
    months = fields.IntField(unique=True)  # 1, 3, 6

    class Meta:
        table = "durations"


class Audience(Model):
    """
    Типы аудиторий для рассылки.
    """
    id = fields.IntField(pk=True)
    code = fields.CharField(50, unique=True)  # "ALL", "ACTIVE", "INACTIVE"
    name = fields.CharField(100)

    class Meta:
        table = "audiences"


class FileType(Model):
    """
    Типы файлов в базе знаний.
    """
    id = fields.IntField(pk=True)
    code = fields.CharField(20, unique=True)  # "TXT", "PDF", "DOCX"
    name = fields.CharField(50)

    class Meta:
        table = "file_types"


class Level(Model):
    """
    Геймификация — уровни пользователя.
    """
    id = fields.IntField(pk=True)
    code = fields.CharField(50, unique=True)  # "NOVICE", "PRACTICER", ...
    name = fields.CharField(100)              # "Новичок", "Практик"...
    xp_required = fields.IntField()

    class Meta:
        table = "levels"


class Experience(Model):
    """
    Опыт пользователя (сегментация).
    """
    id = fields.IntField(pk=True)
    code = fields.CharField(50, unique=True)  # "BEGINNER","SELLER","PRO"
    name = fields.CharField(100)              # читаемое имя

    class Meta:
        table = "experiences"


class Platform(Model):
    """
    Основная площадка пользователя.
    """
    id = fields.IntField(pk=True)
    code = fields.CharField(50, unique=True)  # "WB","OZON","BOTH"
    name = fields.CharField(100)

    class Meta:
        table = "platforms"


class TrafficSource(Model):
    """
    Источники трафика (UTM/метки, рефки).
    """
    id = fields.IntField(pk=True)
    code = fields.CharField(100, unique=True)  # "REF","REELS","AD"
    name = fields.CharField(150)

    class Meta:
        table = "traffic_sources"
