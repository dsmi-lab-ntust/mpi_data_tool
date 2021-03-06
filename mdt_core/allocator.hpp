#ifndef MDT_CORE_ALLOCATOR_HPP_
#define MDT_CORE_ALLOCATOR_HPP_

#include <cstdlib>
#include <new>
#include <limits>

namespace mdt_core {

template <typename T>
struct allocator {
  typedef size_t size_type;
  typedef ptrdiff_t difference_type;
  typedef T * pointer;
  typedef const T * const_pointer;
  typedef T& reference;
  typedef const T& const_reference;
  typedef T value_type;

  template <class U>
  struct rebind {
    typedef allocator<U> other;
  };

  allocator() throw() {
  }

  allocator(const allocator&) throw() {
  }

  template <class U> allocator(const allocator<U>&) throw() {
  }

  ~allocator() throw() {
  }

  pointer allocate(size_type s, void const * = 0) {
    if (s == 0) {
      return NULL;
    }
    pointer tmp = (pointer)malloc(s * sizeof(T));
    if (tmp == NULL) {
      throw std::bad_alloc();
    }
    return tmp;
  }

  void deallocate(pointer p, size_type) {
    free(p);
  }

  size_type max_size() const throw() { 
    return std::numeric_limits<size_t>::max() / sizeof(T); 
  }

  void construct(pointer p, const T& val) {
    new ((void *)p) T(val);
  }

  void destroy(pointer p) {
    p->~T();
  }

  pointer address(reference x) const {
    return &x;
  }

  const_pointer address(const_reference x) const {
    return &x;
  }
};

template <class T, class U>
bool operator==(const allocator<T>&, const allocator<U>&) {
  return false;
}

template <class T, class U>
bool operator!=(const allocator<T>&, const allocator<U>&) {
  return true;
}

}

#endif /* MDT_CORE_ALLOCATOR_HPP_ */
