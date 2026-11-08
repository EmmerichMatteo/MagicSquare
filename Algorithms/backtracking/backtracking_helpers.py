from Entities.matrix import Matrix


def _propagate(
    board: Matrix,
    domains: list[set[int]],
    lines: tuple[tuple[int, ...], ...],
    lines_for_cell: tuple[tuple[int, ...], ...],
) -> bool:
    # Propagate uniqueness and sum constraints until the branch domains stabilize.
    # domains stores allowed cell values; lines lists rows, columns, and diagonals.
    # lines_for_cell maps cells to their lines. Update the board and domains in place.
    # Return False on contradiction, or True when stable; empty cells may remain.
    # Track lines to recheck without duplicates; prioritize cells with one candidate.
    pending = set(range(len(lines)))
    singles = [
        cell for cell, domain in enumerate(domains)
        if board.array[cell] == 0 and len(domain) == 1
    ]

    while singles or pending:
        if singles:
            cell = singles.pop()
            # Multiple deductions may have queued the same cell.
            if board.array[cell] != 0:
                continue
            if not domains[cell]:
                return False
            value = next(iter(domains[cell]))
            board.array[cell] = value
            # Assigning a value changes the remaining sum of every affected line.
            pending.update(lines_for_cell[cell])

            # Enforce global uniqueness, including cells that share no line with this cell.
            for other, domain in enumerate(domains):
                if other == cell:
                    continue
                if board.array[other] == value:
                    return False
                if board.array[other] == 0 and value in domain:
                    domain.remove(value)
                    if not domain:
                        # An empty domain makes this branch invalid.
                        return False
                    pending.update(lines_for_cell[other])
                    if len(domain) == 1:
                        # Removing a value may force further assignments.
                        singles.append(other)
            continue

        # Zeros contribute nothing; remaining_sum must come from the empty cells.
        line = lines[pending.pop()]
        empty = [cell for cell in line if board.array[cell] == 0]
        remaining_sum = board.M - sum(board.array[cell] for cell in line)
        if not empty:
            # A completed line must equal the magic sum.
            if remaining_sum != 0:
                return False
            continue
        if any(not domains[cell] for cell in empty):
            return False

        # With one empty cell, the remaining sum determines its value.
        # Example for 5x5: [16, 9, 12, 23, _] requires 5.
        if len(empty) == 1:
            cell = empty[0]
            if remaining_sum not in domains[cell]:
                return False
            domains[cell] = {remaining_sum}
            singles.append(cell)
            continue

        # Snapshot domain bounds; each reduction queues affected lines until stable.
        # These bounds are necessary but not sufficient: cells may share the same extrema.
        ordered = {cell: sorted(domains[cell]) for cell in empty}
        lower = sum(values[0] for values in ordered.values())
        upper = sum(values[-1] for values in ordered.values())
        if not lower <= remaining_sum <= upper:
            return False

        for cell in empty:
            allowed = set()
            for value in ordered[cell]:
                if len(empty) == 2:
                    # For two cells, require a distinct complement in the other domain.
                    other = empty[1] if cell == empty[0] else empty[0]
                    required = remaining_sum - value
                    if required != value and required in domains[other]:
                        allowed.add(value)
                    continue

                # Assume this value is assigned here; remove this cell from the bounds.
                other_lower = lower - ordered[cell][0]
                other_upper = upper - ordered[cell][-1]
                for other in empty:
                    if other == cell:
                        continue
                    values = ordered[other]
                    # Other cells cannot reuse the candidate value.
                    if len(values) == 1 and values[0] == value:
                        break
                    # If the candidate is a bound of another domain, use the next available value.
                    if values[0] == value:
                        other_lower += values[1] - values[0]
                    if values[-1] == value:
                        other_upper += values[-2] - values[-1]
                else:
                    # The loop else runs only without a break: no other domain became empty.
                    if other_lower <= remaining_sum - value <= other_upper:
                        allowed.add(value)

            if not allowed:
                return False
            if allowed != domains[cell]:
                # A reduced domain may affect previously checked rows, columns, or diagonals.
                # Queue all affected lines again.
                domains[cell] = allowed
                pending.update(lines_for_cell[cell])
                if len(allowed) == 1:
                    singles.append(cell)
                    # Assign the forced value before filtering further cells.
                    break

    # With no pending deductions, the search can choose the next cell.
    return True


def assign_and_forward_check(
    board: Matrix, domains: list[set[int]], cell: int, value: int,
    lines, lines_for_cell
) -> bool:
    # Assign the chosen value and propagate its consequences.
    if value not in domains[cell] or board.array[cell] not in (0, value):
        return False
    if board.array[cell] == value:
        return True

    # Restrict the chosen cell to one value, then propagate all consequences.
    domains[cell] = {value}
    return _propagate(board, domains, lines, lines_for_cell)


def generate_successors(board, domains, cell, values, lines, lines_for_cell):
    # Yield valid branches one at a time after assigning and propagating a value.
    for value in values:
        next_board = Matrix(board.n, board.array)
        next_domains = [domain.copy() for domain in domains]
        if assign_and_forward_check(
            next_board, next_domains, cell, value, lines, lines_for_cell
        ):
            yield next_board, next_domains


def eliminated_candidates(value: int, domains, empty, cell) -> int:
    # Count the candidates removed from other empty cells by this value.
    return sum(value in domains[other] for other in empty if other != cell)
