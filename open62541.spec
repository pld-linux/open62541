# TODO: MQTT
#
# Conditional build:
%bcond_without	apidocs		# API documentation
#
Summary:	Open source C implementation of OPC UA
Summary(pl.UTF-8):	Mająca otwarte źródła, napisana w C implementacja OPC UA
Name:		open62541
Version:	1.3.2
Release:	3
License:	MPL v2.0
Group:		Libraries
#Source0Download: https://github.com/open62541/open62541/releases
Source0:	https://github.com/open62541/open62541/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	9fecf3e64983e372f4c20066180829ea
Patch0:		%{name}-types.patch
Patch1:		%{name}-bpf.patch
Patch2:		%{name}-libwebsockets4.patch
Patch3:		%{name}-visibility.patch
Patch4:		%{name}-rpath.patch
URL:		http://www.open62541.org/
BuildRequires:	cmake >= 3.0
BuildRequires:	libwebsockets-devel
BuildRequires:	openssl-devel
BuildRequires:	p11-kit-devel
BuildRequires:	python3 >= 1:3
BuildRequires:	tpm2-pkcs11-devel
%if %{with apidocs}
BuildRequires:	python3-sphinx_rtd_theme
BuildRequires:	sphinx-pdg >= 2
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
open62541 is an open source and free implementation of OPC UA (OPC
Unified Architecture) written in the common subset of the C99 and
C++98 languages. The library is usable with all major compilers and
provides the necessary tools to implement dedicated OPC UA clients and
servers, or to integrate OPC UA-based communication into existing
applications. open62541 library is platform independent. All
platform-specific functionality is implemented via exchangeable
plugins. Plugin implementations are provided for the major operating
systems.

%description -l pl.UTF-8
open62541 to wolnodostępna, otwarta implementacja OPC UA (OPC Unified
Architecture), napisana we wspólnym podzbiorze języków C99 i C++98.
Biblioteka jest używalna ze wszystkimi głównymi kompilatorami,
dostarcza narzędzia potrzebne do implementacji dedykowanych klientów i
serwerów OPC UA lub integracji komunikacji opartej o OPC UA w
istniejących aplikacjach. Biblioteka open62541 jest niezależna od
platformy. Zała funkcjonalność zależna od platformy jest
implementowana poprzez wymienne wtyczki. Implementacje wtyczek dla
wszystkich głównych systemów są dostarczone.

%package devel
Summary:	Header files for open62541 library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki open62541
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for open62541 library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki open62541.

%package apidocs
Summary:	API documentation for open62541 library
Summary(pl.UTF-8):	Dokumentacja API biblioteki open62541
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for open62541 library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki open62541.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

# not for gcc
%{__sed} -i -e '/check_add_.*-Wno-static-in-inline/d' CMakeLists.txt

%{__sed} -i -e '1s,/usr/bin/env python,%{__python},' \
	tools/*.py \
	tools/nodeset_compiler/nodeset_testing.py

%{__sed} -i -e '1s,/usr/bin/env python3,%{__python3},' \
	tools/certs/create_self-signed.py \
	tools/nodeset_compiler/nodeset_compiler.py

# not executable directly, drop shebangs
%{__sed} -i -e '1s,.*/usr/bin/env python.*,,' \
	tools/nodeset_compiler/{backend_open62541,backend_open62541_nodes,datatypes,nodes,nodeset}.py

%build
install -d build
cd build
# tpm2 support needs pkcs11.h from tpm2-pkcs11, which is in fast p11-kit include file
CFLAGS="%{rpmcflags} -I/usr/include/p11-kit-1/p11-kit -Wno-error=maybe-uninitialized"
LDFLAGS="%{rpmldflags} -L%{_libdir}/pkcs11"
%cmake .. \
	-DCMAKE_INSTALL_INCLUDEDIR=include \
	-DCMAKE_INSTALL_LIBDIR=%{_lib} \
	-DTPM2_LIB=%{_libdir}/pkcs11/libtpm2_pkcs11.so \
	-DUA_BUILD_TOOLS=ON \
	-DUA_ENABLE_DISCOVERY=ON \
	-DUA_ENABLE_ENCRYPTION=MBEDTLS \
	-DUA_ENABLE_ENCRYPTION_TPM2=ON \
	-DUA_ENABLE_JSON_ENCODING=ON \
	-DUA_ENABLE_PUBSUB=ON \
	-DUA_ENABLE_PUBSUB_ENCRYPTION=ON \
	-DUA_ENABLE_PUBSUB_ETH_UADP=ON \
	-DUA_ENABLE_WEBSOCKET_SERVER=ON \
	-DUA_MULTITHREADING=100

# -DUA_ENABLE_DISCOVERY_MULTICAST=ON requires deps/mdnsd
# -DUA_ENABLE_PUBSUB_MQTT requires deps/mqtt-c
# -DUA_NAMESPACE_ZERO=FULL requires deps/ua_nodeset

%{__make}

%if %{with apidocs}
%{__make} doc
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

# tests
%{__rm} $RPM_BUILD_ROOT%{_datadir}/open62541/tools/nodeset_compiler/nodeset_testing.py

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG FEATURES.md README.md
%attr(755,root,root) %{_libdir}/libopen62541.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libopen62541.so.1
%dir %{_datadir}/open62541
%dir %{_datadir}/open62541/tools
%attr(755,root,root) %{_datadir}/open62541/tools/generate_*.py
%dir %{_datadir}/open62541/tools/certs
%attr(755,root,root) %{_datadir}/open62541/tools/certs/create_self-signed.py
%{_datadir}/open62541/tools/certs/localhost.cnf
%dir %{_datadir}/open62541/tools/nodeset_compiler
%attr(755,root,root) %{_datadir}/open62541/tools/nodeset_compiler/nodeset_compiler.py
%{_datadir}/open62541/tools/nodeset_compiler/[!n]*.py
%{_datadir}/open62541/tools/nodeset_compiler/nodes.py
%{_datadir}/open62541/tools/nodeset_compiler/nodeset.py
%{_datadir}/open62541/tools/nodeset_compiler/__pycache__
%{_datadir}/open62541/tools/nodeset_compiler/NodeID_NS0_Base.txt
%doc %{_datadir}/open62541/tools/nodeset_compiler/README.md
%{_datadir}/open62541/tools/schema

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libopen62541.so
%{_includedir}/open62541
%{_includedir}/aa_tree.h
%{_includedir}/ms_stdint.h
%{_includedir}/ziptree.h
%{_pkgconfigdir}/open62541.pc
%{_libdir}/cmake/open62541

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc build/doc/{_images,_static,*.html,*.js}
%endif
