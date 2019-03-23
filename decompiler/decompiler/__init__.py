__all__ = ['mlil_linear', 'mlil_ast']

try:
    from binaryninjaui import ViewType

    from .mlil_linear import MlilLinearViewType

    ViewType.registerViewType(MlilLinearViewType())
except ImportError:
    pass