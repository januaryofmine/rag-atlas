from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Float, cast, literal
from sqlalchemy.types import UserDefinedType


class VectorType(UserDefinedType[list[float]]):
    """Tiny SQLAlchemy adapter for PostgreSQL pgvector's `vector(n)` type.

    The database still uses the real pgvector extension. This adapter keeps the
    code dependency-light while exposing cosine distance as a clear
    method: `Repository.embedding.cosine_distance(query_vector)`.
    """

    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **_: object) -> str:
        return f"vector({self.dimensions})"

    def bind_processor(self, dialect):  # type: ignore[no-untyped-def]
        del dialect

        def process(value: Sequence[float] | None) -> str | None:
            if value is None:
                return None
            if len(value) != self.dimensions:
                raise ValueError(
                    f"expected {self.dimensions} values, got {len(value)}"
                )
            return "[" + ",".join(f"{float(item):.9g}" for item in value) + "]"

        return process

    def bind_expression(self, bindvalue):  # type: ignore[no-untyped-def]
        return cast(bindvalue, self)

    def result_processor(self, dialect, coltype):  # type: ignore[no-untyped-def]
        del dialect, coltype

        def process(value):  # type: ignore[no-untyped-def]
            if value is None:
                return None
            if isinstance(value, list):
                return [float(item) for item in value]
            text = str(value).strip().lstrip("[").rstrip("]")
            return [] if not text else [float(item) for item in text.split(",")]

        return process

    class comparator_factory(UserDefinedType.Comparator):
        def cosine_distance(self, other: Sequence[float]):
            return self.expr.op("<=>", return_type=Float)(
                literal(list(other), type_=self.type)
            )
