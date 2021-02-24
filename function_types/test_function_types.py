from binaryninja import Function, BinaryView, PluginCommand, MediumLevelILOperation, log, Type, FunctionParameter

def fix_printfs(view: BinaryView):
    printf = view.get_symbols_by_name('_printf')
    
    if not printf:
        printf = view.get_symbols_by_name('printf')
    
    if not printf:
        return

    for sym in printf:
        function = view.get_function_at(sym.address)
        if not function:
            continue

        xrefs = view.get_code_refs(function.start)

        for xref in xrefs:
            caller: Function = xref.function

            call_mlil = caller.get_low_level_il_at(xref.address).mlil
            print(call_mlil)
            if call_mlil is None:
                continue

            fmt_operand = call_mlil.params[0]
            if fmt_operand.operation == MediumLevelILOperation.MLIL_VAR:
                log.log_warn(f"Potential format string bug: {fmt_operand.address:x}")
                continue

            elif fmt_operand.operation in (MediumLevelILOperation.MLIL_CONST_PTR, MediumLevelILOperation.MLIL_CONST):
                fmt_address = fmt_operand.constant
                fmt = view.get_ascii_string_at(fmt_address, 2)

                if fmt is None:
                    continue

                fmt_value = fmt.value

            else:
                continue

            specifiers = fmt_value.split('%')
            
            param_types = []

            for specifier in specifiers[1:]:
                if not specifier:
                    continue

                if specifier.startswith('d'):
                    param_types.append(Type.int(4, sign=True))
                elif specifier.startswith('s'):
                    param_types.append(Type.pointer(view.arch, Type.char()))
                elif specifier.startswith('p'):
                    param_types.append(Type.pointer(view.arch, Type.void()))
                else:
                    log.log_warn(f'Unknown format specifier: {specifier}; skipping')
                    param_types.append(Type.pointer(view.arch, Type.void()))

            param_idx = 1
            params = [FunctionParameter(Type.pointer(view.arch, Type.char()), 'fmt')]
            for param in param_types:
                params.append(FunctionParameter(param, f'arg{param_idx}'))
                param_idx += 1

            caller.set_call_type_adjustment(xref.address, Type.function(Type.int(4), params))


PluginCommand.register(
    'Fix up printf signatures',
    'Fix up printf signatures so that the variadic arguments are correctly typed',
    fix_printfs
)