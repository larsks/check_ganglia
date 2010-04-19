%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name:		check-ganglia
Version:	20100419.1
Release:	1%{?dist}
Summary:	Ganglia integration for Nagios.

Group:		Applications/System
License:	GPL
URL:		http://github.com/larsks/check-ganglia
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	python
Requires:	python

%description
Ganglia integration for Nagios.

%prep
%setup -q


%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d $RPM_BUILD_ROOT
python setup.py install --root $RPM_BUILD_ROOT \
	--install-scripts %{_libdir}/nagios/plugins

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)

%{python_sitelib}
%{_libdir}/nagios/plugins/check_ganglia

