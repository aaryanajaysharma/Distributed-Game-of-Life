from mpi4py import MPI
import sys
def count_neighbors(grid, x, y, N, M):
    """Count the live neighbors of a cell."""
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            nx, ny = x + i, y + j
            if 0 <= nx < N and 0 <= ny < M:
                count += grid[nx][ny]
    return count

def update_grid(grid, N, M):
    """Update the grid for the next generation."""
    new_grid = [[0 for _ in range(M)] for _ in range(N)]
    for i in range(N):
        for j in range(M):
            neighbors = count_neighbors(grid, i, j, N, M)
            if grid[i][j] == 1 and neighbors in [2, 3]:
                new_grid[i][j] = 1
            elif grid[i][j] == 0 and neighbors == 3:
                new_grid[i][j] = 1
    return new_grid

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        # Read the grid configuration from the input file
        with open('input.txt', 'r') as file:
            N, M, T = map(int, file.readline().split())
            grid = [list(map(int, line.split())) for line in file.readlines()[:N]]
        # Flatten the grid to a single list of ints
        flat_grid = [cell for row in grid for cell in row]
    else:
        N, M, T = None, None, None
        flat_grid = None
    start_time = MPI.Wtime() if rank == 0 else None
    # Broadcasting the grid size and number of generations
    N, M, T = comm.bcast((N, M, T), root=0)

    # Distributing the work (simple 1D decomposition)
    rows_per_process = N // size
    start_row = rank * rows_per_process
    end_row = N if rank == size - 1 else (rank + 1) * rows_per_process

    # Distribute the grid to all processes
    if rank == 0:
        for i in range(1, size):
            start = i * rows_per_process
            end = N if i == size - 1 else (i + 1) * rows_per_process
            comm.send(grid[start:end], dest=i)
    else:
        grid = comm.recv(source=0)

    # Simulating the generations
    for _ in range(T):
        # Compute new state for assigned rows
        local_grid = update_grid(grid, end_row - start_row, M)
        grid = local_grid

        # Communication between processes if needed for edge rows

    # Gathering the results at root
    if rank == 0:
        final_grid = grid
        for i in range(1, size):
            final_grid += comm.recv(source=i)
    else:
        comm.send(grid, dest=0)
    if rank == 0:
        end_time = MPI.Wtime()
        print(f"Execution Time: {end_time - start_time} seconds")
    # Printing the final grid

    # Printing the final grid
    with open('my_output.txt', 'w') as f:
        sys.stdout = f
        if rank == 0:
            for row in final_grid:
                print(' '.join(map(str, row)))
                
if __name__ == '__main__':
    main()
