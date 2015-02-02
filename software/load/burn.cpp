#include <mpi.h>
#include <stdlib.h>
#include <iostream>


int main(int argc, char ** argv)
{
        MPI_Init(&argc, &argv);

        int rank;
        MPI_Comm_rank(MPI_COMM_WORLD, &rank);

        if( rank == 0 )
                std::cout << "starting job" << std::endl;

        double start_time = MPI_Wtime();

        // How much time should we burn?
        double m_time = 60;
        if( argc == 2)
                m_time = atof(argv[1]);

        double * data = new double[100000];

        double end_time = MPI_Wtime();
        while( end_time - start_time < m_time )
        {
                end_time = MPI_Wtime();
                int index = static_cast<int>(end_time - start_time);
                index = index%100000;
                data[index] = end_time - start_time;
        }

        delete [] data;


        MPI_Finalize();

        return 0;
}
