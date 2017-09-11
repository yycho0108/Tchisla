Tchisla

---

Attempt to provide a general solution to solving [Tchisla](https://itunes.apple.com/us/app/tchisla-number-puzzle/id1100623105?mt=8).

In the current approach, this is the same as creating a dynamic path according to the following heuristic:

<img src="http://latex.codecogs.com/png.latex?x&space;=&space;f_b(f_u(x_l),f_u(x_r)),&space;f_b&space;\in&space;B,&space;f_u&space;\in&space;U,&space;x_l,x_r&space;\in&space;X" title="x = f_b(f_u(x_l),f_u(x_r)), f_b \in B, f_u \in U, x_l,x_r \in X" />

as

<img src="http://latex.codecogs.com/png.latex?c(x)&space;=&space;c(x_l)&space;&plus;&space;c(x_r)" title="c(x) = c(x_l) + c(x_r)" />

in an iterative procedure.


See the [implementation](main.py) for details and more documentation.
