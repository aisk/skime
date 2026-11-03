;; map and for-each are written in Scheme so that their callbacks run on the
;; VM. Calling back into the VM from Python would consume the Python stack
;; for every nested call.

(define map
  (let ((apply apply)
        (reverse reverse)
        (cons cons)
        (done? %lists-done?)
        (cars %cars)
        (cdrs %cdrs))
    (lambda (proc list1 . lists)
      (let loop ((lists (cons list1 lists))
                 (result '()))
        (if (done? lists 'map)
            (reverse result)
            (loop (cdrs lists)
                  (cons (apply proc (cars lists)) result)))))))

(define for-each
  (let ((apply apply)
        (cons cons)
        (done? %lists-done?)
        (cars %cars)
        (cdrs %cdrs))
    (lambda (proc list1 . lists)
      (let loop ((lists (cons list1 lists)))
        (if (done? lists 'for-each)
            '()
            (begin
              (apply proc (cars lists))
              (loop (cdrs lists))))))))
