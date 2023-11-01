# Shared object version of libcrypt.
%global soc 1
%global sol 1
%global sof 0
%global sov %{soc}.%{sol}.%{sof}

# Add generation of HMAC checksums of the final stripped
# binaries.  %%define with lazy globbing is used here
# intentionally, because using %%global does not work.
%define __spec_install_post                                 \
%{?__debug_package:%{__debug_install_post}}                 \
%{__arch_install_post}                                      \
%{__os_install_post}                                        \
%{_bindir}/fipshmac %{buildroot}/%{_lib}/libcrypt.so.%{sov} \
%{__ln_s} .libcrypt.so.%{sov}.hmac                          \\\
  %{buildroot}/%{_lib}/.libcrypt.so.%{soc}.hmac             \
%{nil}


Name:           libxcrypt
Version:        4.1.1
Release:        6%{?dist}
Summary:        Extended crypt library for DES, MD5, Blowfish and others

# For explicit license breakdown, see the
# LICENSING file in the source tarball.
License:        LGPLv2+ and BSD and Public Domain
URL:            https://github.com/besser82/%{name}
Source0:        %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Patch1: libxcrypt-rh1612157.patch
Patch2: libxcrypt-rh1613537.patch
# fix for salt interoperability issue: https://github.com/besser82/libxcrypt/pull/106
Patch3: libxcrypt-rh1899716.patch

BuildRequires:  fipscheck
BuildRequires:  libtool

Requires:       glibc%{_isa}          >= 2.26.9000-46

# We do not need to keep this forever.
%if 0%{?fedora} && 0%{?fedora} <= 31
# Inherited from former libcrypt package.
Obsoletes:      libcrypt-nss          <= 2.26.9000-33

# Obsolete former libcrypt properly.
Obsoletes:      libcrypt              <= 2.26.9000-46

# Provide virtual libcrypt as it has been done
# by former libcrypt{,-nss} packages from glibc.
Provides:       libcrypt              == 2.26.9000-46.1
Provides:       libcrypt%{?_isa}      == 2.26.9000-46.1
%endif

%description
libxcrypt is a modern library for one-way hashing of passwords.  It
supports DES, MD5, SHA-2-256, SHA-2-512, and bcrypt-based password
hashes, and provides the traditional Unix 'crypt' and 'crypt_r'
interfaces, as well as a set of extended interfaces pioneered by
Openwall Linux, 'crypt_rn', 'crypt_ra', 'crypt_gensalt',
'crypt_gensalt_rn', and 'crypt_gensalt_ra'.

libxcrypt is intended to be used by login(1), passwd(1), and other
similar programs; that is, to hash a small number of passwords during
an interactive authentication dialogue with a human.  It is not
suitable for use in bulk password-cracking applications, or in any
other situation where speed is more important than careful handling of
sensitive data.  However, it *is* intended to be fast and lightweight
enough for use in servers that must field thousands of login attempts
per minute.

On Linux-based systems, by default libxcrypt will be binary backward
compatible with the libcrypt.so.1 shipped as part of the GNU C Library.
This means that all existing binary executables linked against glibc's
libcrypt should work unmodified with this library's libcrypt.so.1.  We
have taken pains to provide exactly the same "symbol versions" as were
used by glibc on various CPU architectures, and to account for the
variety of ways in which the Openwall extensions were patched into
glibc's libcrypt by some Linux distributions.  (For instance,
compatibility symlinks for SuSE's "libowcrypt" are provided.)

However, the converse is not true: programs linked against libxcrypt
will not work with glibc's libcrypt.  Also, programs that use certain
legacy APIs supplied by glibc's libcrypt ('encrypt', 'encrypt_r',
'setkey', 'setkey_r', and 'fcrypt') cannot be compiled against libxcrypt.


%package        devel
Summary:        Development files for %{name}

Requires:       %{name}%{?_isa}       == %{version}-%{release}
Requires:       glibc-devel%{?_isa}   >= 2.26.9000-46
Requires:       glibc-headers%{?_isa} >= 2.26.9000-46
Conflicts:	man-pages < 4.15-3

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        static
Summary:        Static library for -static linking with %{name}

Requires:       %{name}-devel%{?_isa} == %{version}-%{release}
Requires:       glibc-static%{?_isa}  >= 2.26.9000-46

%description    static
This package contains the libxcrypt static libraries for -static
linking.  You don't need this, unless you link statically, which
is highly discouraged.


%prep
%autosetup -p 1
%{_bindir}/autoreconf -fiv


%build
%configure                     \
  --libdir=/%{_lib}            \
  --disable-silent-rules       \
  --enable-shared              \
  --enable-static              \
  --disable-failure-tokens     \
  --enable-hashes=all          \
  --enable-obsolete-api=glibc  \
  --with-pkgconfigdir=%{_libdir}/pkgconfig
%make_build


%install
%make_install

# Get rid of libtool crap.
%{_bindir}/find %{buildroot} -name '*.la' -print -delete

# Install documentation to shared %%_pkgdocdir.
%{__install} -Dpm 0644 -t %{buildroot}%{_pkgdocdir} \
  ChangeLog NEWS README THANKS TODO


%check
%make_build check || \
  {
    rc=$?;
    echo "-----BEGIN TESTLOG-----";
    %{__cat} test-suite.log;
    echo "-----END TESTLOG-----";
    exit $rc;
  }


%ldconfig_scriptlets


%files
%license AUTHORS COPYING.LIB LICENSING
%doc %dir %{_pkgdocdir}
%doc %{_pkgdocdir}/NEWS
%doc %{_pkgdocdir}/README
%doc %{_pkgdocdir}/THANKS
/%{_lib}/.libcrypt.so.%{soc}.hmac
/%{_lib}/.libcrypt.so.%{sov}.hmac
/%{_lib}/libcrypt.so.%{soc}
/%{_lib}/libcrypt.so.%{sov}
%{_mandir}/man5/crypt.5.*


%files          devel
%doc %{_pkgdocdir}/ChangeLog
%doc %{_pkgdocdir}/TODO
/%{_lib}/libcrypt.so
%{_includedir}/crypt.h
%{_libdir}/pkgconfig/libcrypt.pc
%{_libdir}/pkgconfig/%{name}.pc
%{_mandir}/man3/crypt.3.*
%{_mandir}/man3/crypt_r.3.*
%{_mandir}/man3/crypt_ra.3.*
%{_mandir}/man3/crypt_rn.3.*
%{_mandir}/man3/crypt_gensalt.3.*

%files          static
/%{_lib}/libcrypt.a


%changelog
* Thu Apr 29 2021 Stanislav Zidek <szidek@redhat.com> - 4.1.1-6
+ libxcrypt-4.1.1-6
- Rebuilt with fixed binutils (#1954438)

* Wed Apr  7 2021 Stanislav Zidek <szidek@redhat.com> - 4.1.1-5
- Fixed salt interoperability issue (#1899716)

* Wed Aug  8 2018 Florian Weimer <fweimer@redhat.com> - 4.1.1-4
- Move development panpages to libxcrypt-devel (#1613824)

* Wed Aug  8 2018 Florian Weimer <fweimer@redhat.com> - 4.1.1-3
- Change crypt, crypt_r to return NULL on failure (#1613537)

* Wed Aug  8 2018 Florian Weimer <fweimer@redhat.com> - 4.1.1-2
- Add manpages aliases for crypt, crypt_r, crypt_ra (#1612157)

* Wed Aug 01 2018 Björn Esser <besser82@fedoraproject.org> - 4.1.1-1
- New upstream release

* Fri Jul 13 2018 Björn Esser <besser82@fedoraproject.org> - 4.1.0-1
- New upstream release

* Fri Jul 13 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.1-6
- Make testsuite fail on error again
- Update patch0 with more upstream fixes

* Fri Jul 13 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.1-5
- Add patch to update to recent development branch
- Re-enable SUNMD5 support as it is BSD licensed now
- Build compatibility symbols for glibc only
- Skip failing testsuite once

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Florian Weimer <fweimer@redhat.com> - 4.0.1-3
- Remove CDDL from license list (#1592445)

* Fri Jun 29 2018 Florian Weimer <fweimer@redhat.com> - 4.0.1-2
- Remove SUNMD5 support (#1592445)

* Wed May 16 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.1-1
- New upstream release

* Sat Feb 17 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-5
- Switch to %%ldconfig_scriptlets

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Feb 01 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-3
- Add patch to fix unintialize value in badsalt test

* Wed Jan 31 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-2
- Add patch to fix bcrypt test with GCC8

* Sat Jan 27 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-1
- New upstream release

* Mon Jan 22 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.0.0-0.204.20180120git3436e7b
- Fix Obsoletes

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-0.203.20180120git3436e7b
- Update to new snapshot fixing cast-align

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-0.202.20180120gitde99d27
- Update to new snapshot (rhbz#1536752)

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-0.201.20171109git15447aa
- Use archful Obsoletes for libcrypt
- Add versioned Requires on glibc packages not shipping libcrypt
- Add comments about the packaging logic for replacing former libcrypt

* Fri Jan 12 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-0.200.20171109git15447aa
- Initial import (rhbz#1532794)
- Add Obsoletes/Provides for libcrypt

* Wed Jan 10 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-0.101.20171109git15447aa
- Fix style of %%git_{rel,ver}

* Tue Jan 09 2018 Björn Esser <besser82@fedoraproject.org> - 4.0.0-0.100.git20171109.15447aa
- Initial rpm release (rhbz#1532794)
- Start revision at 0.100 to superseed builds from COPR
