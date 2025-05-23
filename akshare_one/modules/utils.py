def convert_xieqiu_symbol(symbol: str) -> str:
    """
    Convert Symbol (600000) to XueQiu Symbol (SH600000)
    """
    if symbol.startswith("6"):
        return f"SH{symbol}"
    elif symbol.startswith("0") or symbol.startswith("3"):
        return f"SZ{symbol}"
    else:  # TODO: add more cases
        return symbol
