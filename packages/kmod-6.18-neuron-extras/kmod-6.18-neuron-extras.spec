%global kmajor 6.18
%global kernel_sources %{_cross_usrsrc}/kernels/6.18
%global _cross_kmoddir %{_cross_libdir}/modules/%{kmajor}
%global _ko ko

Name: %{_cross_os}kmod-6.18-neuron-extras
Version: 1.0.0
Release: 1%{?dist}
Epoch: 1
Summary: Extra Neuron driver modules for the Linux kernel
License: MIT AND GPL-2.0-only AND (GPL-2.0-only OR BSD-2-Clause) AND (GPL-2.0 OR Linux-OpenIB) AND (((GPL-2.0 WITH Linux-syscall-note) OR BSD-2-Clause))

# Neuron driver 2.x.7372.0
Source1: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.7372.0.noarch.rpm/e82516a77ab54f1c651a1f160e3a67b1cbca8bef391d78a6c683d6fc22442c8ee17df9d3fae1392ca8cffa676bb966b7088c32e634894ba142d83bef58dd2d81/aws-neuronx-dkms-2.x.7372.0.noarch.rpm
# Neuron driver 2.x.7693.0
Source2: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.7693.0.noarch.rpm/4411e3d28bc307bd096408f72f9c3d9e3edcadcbeab3ca409b0f94041ac1f589120353edfb1e11c45ff5a5421808297a308f18a6ac687459abe8c5e985653d3f/aws-neuronx-dkms-2.x.7693.0.noarch.rpm
# Neuron driver 2.x.8072.0
Source3: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.8072.0.noarch.rpm/d96bd0fe73482684c97faae6f779bfa8a84e9b9ca09f796031d409322550fb1744a38e6c54f5fcc8c1221f051cf04f518694876ea825722f5ed7895c2e8bb22a/aws-neuronx-dkms-2.x.8072.0.noarch.rpm
# Neuron driver 2.x.8689.0
Source4: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.8689.0.noarch.rpm/5d3ce7f81858d5aae62279369bce72e041dd321f71146a4ab8e61f9230f3965323f9c9230547476614f1c334b84c59edbd892524e2a87c35b46960a044502e9f/aws-neuronx-dkms-2.x.8689.0.noarch.rpm
Source5: gpgkey-00FA2C1079260870A76D2C285749CAD8646D9185.asc

# Neuron driver patches for kernel 6.18 compatibility.
Patch2001: 2001-Rename-struct-mempool-to-struct-neuron_mempool.patch

BuildRequires: %{_cross_os}kernel-6.18-devel
Requires: %{_cross_os}kernel-6.18

Requires: %{_cross_os}variant-platform(aws)
Conflicts: %{_cross_os}variant-flavor(nvidia)
Conflicts: %{_cross_os}variant-flavor(nvidia-fips)

%description
%{summary}.

%prep
rpmkeys --import %{S:5} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:1} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:2} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:3} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:4} --dbpath "${PWD}/rpmdb"
rm -rf "${PWD}/rpmdb"

# 2.x.7372.0 neuron driver
rpm2cpio %{S:1} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_7372 \;
rm -r usr
pushd neuron_2x_7372
%patch -P 2001 -p1
popd

# 2.x.7693.0 neuron driver
rpm2cpio %{S:2} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_7693 \;
rm -r usr
pushd neuron_2x_7693
%patch -P 2001 -p1
popd

# 2.x.8072.0 neuron driver
rpm2cpio %{S:3} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_8072 \;
rm -r usr
pushd neuron_2x_8072
%patch -P 2001 -p1
popd

# 2.x.8689.0 neuron driver
rpm2cpio %{S:4} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_8689 \;
rm -r usr

%global kmake %{shrink: \
make -s \
  ARCH="%{_cross_karch}" \
  CROSS_COMPILE="%{_cross_target}-" \
  INSTALL_HDR_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_STRIP=1 \
  %{nil}}

%build
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_7372
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_7693
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_8072
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_8689

%install
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_7372/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_7693/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8072/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8689/
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_7372 M=%{_builddir}/neuron_2x_7372 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_7693 M=%{_builddir}/neuron_2x_7693 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_8072 M=%{_builddir}/neuron_2x_8072 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_8689 M=%{_builddir}/neuron_2x_8689 modules_install
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_7372/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_7372/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_7693/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_7693/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_8072/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8072/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_8689/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8689/

%files
%{_cross_attribution_file}
%{_cross_libexecdir}/neuron/neuron_2x_7372/neuron.%{_ko}
%{_cross_libexecdir}/neuron/neuron_2x_7693/neuron.%{_ko}
%{_cross_libexecdir}/neuron/neuron_2x_8072/neuron.%{_ko}
%{_cross_libexecdir}/neuron/neuron_2x_8689/neuron.%{_ko}

%changelog
