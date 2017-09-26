(define (problem BLOCKS-6-2) (:domain blocks)
(:objects

	b - block
	d - block
	c - block
	a - block

	(:private a1
		a1 - agent
	)

	(:private a2
		a2 - agent
	)
)
(:init
	(handempty a1)
	(handempty a2)
	(clear b)
	(clear d)
	(ontable a)
	(ontable c)
	(on b a)
	(on d c)
)
(:goal
	(and
		(on a d)
		(on c b)
	)
)
)